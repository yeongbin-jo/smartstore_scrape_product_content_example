from typing import Any

import orjson
import requests
from pylab_sdk import get_latest_agents
from parsel import Selector
import sys

USER_AGENT = get_latest_agents('macOS')


def scrape_smartstore_content(url: str) -> Any:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    res = session.get(url)
    sig = '<script>window.__PRELOADED_STATE__='
    start_idx = res.text.rfind(sig)
    end_idx = res.text.find('</script>', start_idx)
    obj = orjson.loads(res.text[start_idx + len(sig):end_idx])

    # product > A > id
    # product > A > channel > channelUid
    # product > A > productNo
    product_id = obj['product']['A']['id']
    channel_uid = obj['product']['A']['channel']['channelUid']
    product_no = obj['product']['A']['productNo']

    res = session.get(f'https://brand.naver.com/n/v2/channels/{channel_uid}/products/{product_id}/contents/{product_no}/PC')
    result = res.json()

    content = result['renderContent']
    selector = Selector(text=content)
    return selector.xpath('//img/@data-src').getall()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        url = 'https://brand.naver.com/bodyluv/products/9871181574'
    else:
        url = sys.argv[1]
    print(scrape_smartstore_content(url))
