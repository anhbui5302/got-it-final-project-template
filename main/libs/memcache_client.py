import math

from memcache import Client

from main.libs.log import ServiceLogger

CHUNKS_KEY_SUFFIX = 'chunks'

# memcache.SERVER_MAX_VALUE_LENGTH is 1024 * 1024 = 1048576,
# but for some reason, the actual max length can be lower, and we
# can encounter the error "SERVER_ERROR object too large for cache"
# with the logic to split a large value into chunks below. So here
# we use the max length of 1024 * 1000 to have some extra spaces.
SERVER_MAX_VALUE_LENGTH = 1_024_000

logger = ServiceLogger(__name__)


class MemcacheClient(Client):
    def __init__(self, *args, **kwargs):
        self._prefix_key = kwargs.pop('prefix_key', '')
        super().__init__(*args, **kwargs)

    def _make_key(self, key):
        return self._prefix_key + key

    def set(self, key, val, *args, **kwargs):
        if isinstance(val, (bytes, str)) and len(val) > SERVER_MAX_VALUE_LENGTH:
            # Slice the large data into chunks of data
            number_of_chunks = math.ceil(len(val) / SERVER_MAX_VALUE_LENGTH)
            chunks_map = {}
            for i in range(number_of_chunks):
                chunk_key = f'{key}:{i}'
                chunks_map[chunk_key] = val[
                    i * SERVER_MAX_VALUE_LENGTH : (i + 1) * SERVER_MAX_VALUE_LENGTH
                ]

            failed_keys = self.set_multi(chunks_map)
            status_code = self.set(
                key=f'{key}:{CHUNKS_KEY_SUFFIX}', val=number_of_chunks
            )

            # Caching is successful if only if both operations above are successful
            is_success = len(failed_keys) == 0 and status_code
            if not is_success:
                # If caching data is not successful then delete the current cached data
                logger.warning(message=f'Caching for the key "{key}" failed')
                self.delete(key=key)
                self.delete(key=f'{key}:{CHUNKS_KEY_SUFFIX}')
        else:
            self.delete(key=f'{key}:{CHUNKS_KEY_SUFFIX}')
            is_success = super().set(
                self._make_key(key),
                val,
                *args,
                **kwargs,
            )
            if not is_success:
                logger.warning(message=f'Caching for the key "{key}" failed')
                self.delete(key=key)

        return is_success

    def get(self, key):
        chunks_key = f'{key}:{CHUNKS_KEY_SUFFIX}'
        number_of_chunks = super().get(self._make_key(chunks_key))
        if number_of_chunks:
            chunk_keys = [f'{key}:{i}' for i in range(number_of_chunks)]

            # Get the value
            cached_values = self.get_multi(keys=chunk_keys).items()
            cached_values = sorted(
                cached_values,
                key=lambda x: int(x[0].split(':')[-1]),
            )
            value = None
            for _, chunk_value in cached_values:
                if not value:
                    value = '' if isinstance(chunk_value, str) else b''

                value += chunk_value
        else:
            value = super().get(
                self._make_key(key),
            )

        return value

    def delete(self, key, *args, **kwargs):
        return super().delete(
            self._make_key(key),
            *args,
            **kwargs,
        )

    def get_multi(self, keys, *_, **__):
        return super().get_multi(
            keys,
            key_prefix=self._prefix_key,
        )

    def set_multi(self, mapping, key_prefix='', *args, **kwargs):
        return super().set_multi(
            mapping,
            key_prefix=self._prefix_key,
            *args,
            **kwargs,
        )
