import asyncio
import json
from asyncio import create_task
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
from csetutils.flask.logging import get_logging

from service.persist.redis import RedisCache
from service.utils.functions import get_fld_by_domain_name


class SimilarWeb:
    def __init__(self, url, api_key, redis_cache: RedisCache):
        self.url = url
        self.api_key = api_key
        self._redis_cache = redis_cache
        self.ttl = 30 * 24 * 60 * 60  # 30 days
        self._logger = get_logging()

    def _get_month_before_last(self) -> str:
        today = datetime.now()
        today_minus_two_months = today - timedelta(days=63)
        return today_minus_two_months.strftime('%Y-%m')

    def _get_higher_rank(self, rank1, rank2) -> int:
        rank1 = int(float(rank1))
        rank2 = int(float(rank2))
        if rank1 <= 0:
            return rank2
        if rank2 <= 0:
            return rank1
        if rank1 < rank2:
            return rank1
        else:
            return rank2

    async def _get_ranks_for_domain(self, domain: str):
        redis_value = self._redis_cache.get(f'{domain}_similar_web')
        if redis_value is not None:
            return json.loads(redis_value)
        global_rank_task = create_task(self.get_rank(domain=domain, country=None))
        country_rank_us_task = create_task(self.get_rank(domain=domain, country='us'))
        country_rank_in_task = create_task(self.get_rank(domain=domain, country='in'))
        global_rank = await global_rank_task
        country_rank_us = await country_rank_us_task
        country_rank_in = await country_rank_in_task
        redis_value = {
            'global_rank': global_rank,
            'country_rank_us': country_rank_us,
            'country_rank_in': country_rank_in
        }
        # Only store in redis if all country ranks are resolved properly.
        # A rank of 0 indicates an unexpected behavior from similar web api
        if global_rank != 0 and country_rank_us != 0 and country_rank_in != 0:
            self._redis_cache.set(redis_key=f'{domain}_similar_web', redis_value=json.dumps(redis_value), ttl=self.ttl)
        else:
            self._logger.info('Skipping redis save for similarweb due to unexpected api behavior')
        return redis_value

    async def get_all_ranks(self, domain: str) -> dict:
        domain_ranks = await self._get_ranks_for_domain(domain)
        base_domain = get_fld_by_domain_name(domain)
        if base_domain == domain:
            return domain_ranks
        base_domain_ranks = await self._get_ranks_for_domain(base_domain)
        return {
            'global_rank': self._get_higher_rank(base_domain_ranks['global_rank'], domain_ranks['global_rank']),
            'country_rank_us': self._get_higher_rank(base_domain_ranks['country_rank_us'], domain_ranks['country_rank_us']),
            'country_rank_in': self._get_higher_rank(base_domain_ranks['country_rank_in'], domain_ranks['country_rank_in'])
        }

    async def get_rank(self, domain: str, country: Optional[str]) -> int:
        params = {'api_key': self.api_key, 'start_date': self._get_month_before_last(),
                  'end_date': self._get_month_before_last(), 'main_domain_only': 'true',
                  'format': 'json'}
        rank_type = 'global-rank'
        if country is not None:
            params['country'] = country
            rank_type = 'country-rank'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.url}/v1/website/{domain}/{rank_type}/{rank_type}',
                                       params=params, headers={'Accept': 'Application/json'}) as resp:
                    if resp.status == 200:
                        response_data = await resp.json()
                        if rank_type == 'global-rank':
                            return int(response_data['global_rank'][0]['global_rank'])
                        else:
                            return int(response_data['country_rank'][0]['country_rank'])
                    elif resp.status == 404:
                        response_data = await resp.json()
                        if response_data.get('meta', {}).get('error_code', 0) == 401:
                            self._logger.info(f'No data found for domain: {domain} in similarweb')
                            return -1
                        else:
                            self._logger.error(f'Expected 200 but obtained status code: {404} from similarweb. Response data: {response_data}')
                    else:
                        response_data = await resp.text()
                        self._logger.error(f'Obtained status code {resp.status} from similar web. Response data: {response_data}')
                    return 0
        except asyncio.TimeoutError:
            self._logger.exception('similar web request timeout')
            return 0
        except Exception:
            self._logger.exception('Exception calling similarweb api')
        return 0
