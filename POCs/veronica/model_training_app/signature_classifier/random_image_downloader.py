import httpx
import asyncio
import random

url = 'https://picsum.photos/{}/{}'
import cgi

location = './test_imgs/other/'


async def call_url(session):
    w = random.randint(75, 300)
    h = random.randint(75, 300)
    i_url = url.format(w, h)
    response = await session.request(method='GET', url=i_url, follow_redirects=True, timeout=30)
    if response.status_code == 200:
        value, params = cgi.parse_header(response.headers['content-disposition'])
        name = params['filename']
        with open(location + name, 'wb') as f:
            f.write(response.content)
    return response.url, response.status_code


from tqdm import tqdm


async def main():
    async with httpx.AsyncClient() as session:
        tasks = [call_url(session) for x in range(900)]
        pbar = tqdm(total=len(tasks))
        for f in asyncio.as_completed(tasks):
            i_url, res_code = await f
            pbar.set_description(f'{i_url} => [{res_code}]')
            pbar.update()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
