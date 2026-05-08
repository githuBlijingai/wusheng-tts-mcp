import os
import httpx
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
import argparse

API_KEY = os.getenv('WUSOUND_API_KEY', '')
API_BASE_URL = os.getenv('WUSOUND_API_BASE_URL', 'https://v1.wusound.cn')
HOST = os.getenv('MCP_HOST', '0.0.0.0')
PORT = int(os.getenv('MCP_PORT', '8000'))

mcp = FastMCP("悟声语音合成服务")


class WuSoundClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        with httpx.Client(timeout=60.0) as client:
            response = client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    def get_voices(self, from_type: Optional[str] = None, show_market: bool = False) -> Dict[str, Any]:
        params = {'showMarket': show_market}
        if from_type:
            params['from'] = from_type
        return self._request('GET', '/api/voice', params=params)

    def get_voice_detail(self, voice_id: str) -> Dict[str, Any]:
        return self._request('GET', f'/api/voice/{voice_id}')

    def create_voice(self, name: str, prompt: str, model_version: str = 'v2.0',
                    language: str = 'auto', description: Optional[str] = None,
                    avatar: Optional[str] = None, vocal_filter: bool = False,
                    lora: Optional[str] = None) -> Dict[str, Any]:
        data = {
            'name': name, 'prompt': prompt, 'modelVersion': model_version,
            'language': language, 'vocalFilter': vocal_filter
        }
        if description:
            data['description'] = description
        if avatar:
            data['avatar'] = avatar
        if lora:
            data['lora'] = lora
        return self._request('POST', '/api/voice', json=data)

    def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        return self._request('DELETE', f'/api/voice/{voice_id}')

    def add_voice_style(self, voice_id: str, prompt: str, name: str,
                        description: Optional[str] = None, language: str = 'auto',
                        vocal_filter: bool = True) -> Dict[str, Any]:
        data = {'prompt': prompt, 'name': name, 'language': language, 'vocalFilter': vocal_filter}
        if description:
            data['description'] = description
        return self._request('POST', f'/api/voice/{voice_id}/prompt', json=data)

    def delete_voice_style(self, voice_id: str, prompt_id: str) -> Dict[str, Any]:
        return self._request('DELETE', f'/api/voice/{voice_id}/prompt/{prompt_id}')

    def get_voice_share_id(self, voice_id: str) -> Dict[str, Any]:
        return self._request('GET', f'/api/voice/{voice_id}/share')

    def add_voice_by_share(self, share_id: str) -> Dict[str, Any]:
        return self._request('POST', '/api/voice/import', json={'shareId': share_id})

    def upload_voice_conversion_audio(self, audio: str) -> Dict[str, Any]:
        return self._request('POST', '/api/tts/upload-audio', json={'audio': audio})

    def simple_generate(self, voice_id: str, text: str, prompt_id: str = 'default',
                       preset: str = 'balance', language: str = 'auto', speech_rate: float = 1.0,
                       break_clone: bool = True, vivid: bool = False,
                       emo_switch: Optional[List[int]] = None, flash: bool = False,
                       stream: bool = False, seed: int = -1, srt: bool = False) -> Dict[str, Any]:
        data = {
            'voiceId': voice_id, 'text': text, 'promptId': prompt_id, 'preset': preset,
            'language': language, 'speechRate': speech_rate, 'break_clone': break_clone,
            'vivid': vivid, 'flash': flash, 'stream': stream, 'seed': seed, 'srt': srt
        }
        if emo_switch:
            data['emo_switch'] = emo_switch
        return self._request('POST', '/api/tts/simple-generate', json=data)

    def create_async_generation(self, contents: List[Dict[str, Any]], srt: bool = False) -> Dict[str, Any]:
        return self._request('POST', '/api/tts/generate', json={'contents': contents, 'srt': srt})

    def get_async_tasks(self, limit: int = 20, offset: int = 0, status: Optional[str] = None) -> Dict[str, Any]:
        params = {'limit': limit, 'offset': offset}
        if status:
            params['status'] = status
        return self._request('GET', '/api/tts/generate', params=params)

    def get_async_task_detail(self, task_id: str) -> Dict[str, Any]:
        return self._request('GET', f'/api/tts/generate/{task_id}')

    def delete_async_task(self, task_id: str) -> Dict[str, Any]:
        return self._request('DELETE', f'/api/tts/generate/{task_id}')

    def get_account_info(self) -> Dict[str, Any]:
        return self._request('GET', '/api/account/info')


client = WuSoundClient(API_KEY)


@mcp.tool()
def get_voice_list(from_type: Optional[str] = None, show_market: bool = False):
    """获取语音角色列表"""
    result = client.get_voices(from_type=from_type, show_market=show_market)
    voices = result.get('data', [])
    return {
        'summary': f"共找到 {len(voices)} 个语音角色",
        'voices': [
            {
                'id': v.get('id'),
                'name': v.get('name'),
                'status': v.get('status'),
                'version': v.get('version'),
                'from': v.get('from'),
                'description': v.get('metadata', {}).get('description', '')
            }
            for v in voices
        ]
    }


@mcp.tool()
def get_voice_detail(voice_id: str):
    """获取指定ID的语音角色详情"""
    result = client.get_voice_detail(voice_id)
    voice = result.get('data', {})
    styles = voice.get('metadata', {}).get('prompts', [])
    return {
        'summary': f"角色「{voice.get('name')}」共有 {len(styles)} 个风格",
        'voice': {
            'id': voice.get('id'),
            'name': voice.get('name'),
            'status': voice.get('status'),
            'version': voice.get('version'),
            'styles': [{'id': s.get('id'), 'name': s.get('name')} for s in styles]
        }
    }


@mcp.tool()
def generate_speech(voice_id: str, text: str, prompt_id: str = 'default',
                   preset: str = 'balance', language: str = 'auto', speech_rate: float = 1.0):
    """同步生成语音"""
    result = client.simple_generate(
        voice_id=voice_id, text=text, prompt_id=prompt_id,
        preset=preset, language=language, speech_rate=speech_rate
    )
    data = result.get('data', {})
    return {
        'summary': f"成功生成音频，消耗 {data.get('credit_used', 0)} 点数",
        'audio_url': data.get('audio'),
        'stream_url': data.get('streamUrl'),
        'credit_used': data.get('credit_used')
    }


@mcp.tool()
def create_multi_voice_generation(contents: List[Dict[str, Any]], srt: bool = False):
    """创建多角色语音生成任务（异步）"""
    formatted_contents = [
        {
            'voiceId': c.get('voice_id'),
            'text': c.get('text'),
            'promptId': c.get('prompt_id', 'default'),
            'preset': c.get('preset', 'balance'),
            'language': c.get('language', 'auto'),
            'speechRate': c.get('speech_rate', 1.0)
        }
        for c in contents
    ]
    result = client.create_async_generation(contents=formatted_contents, srt=srt)
    task = result.get('data', {})
    return {
        'summary': f"成功创建异步生成任务，任务ID: {task.get('id')}",
        'task_id': task.get('id'),
        'status': task.get('status')
    }


@mcp.tool()
def get_generation_tasks(limit: int = 20, offset: int = 0, status: Optional[str] = None):
    """获取异步生成任务列表"""
    result = client.get_async_tasks(limit=limit, offset=offset, status=status)
    tasks = result.get('data', [])
    return {
        'summary': f"共找到 {len(tasks)} 个生成任务",
        'tasks': [
            {'id': t.get('id'), 'status': t.get('status'),
             'characters': t.get('metadata', {}).get('characters', 0)}
            for t in tasks
        ]
    }


@mcp.tool()
def get_generation_task_detail(task_id: str):
    """获取指定ID的异步生成任务详情"""
    result = client.get_async_task_detail(task_id)
    task = result.get('data', {})
    contents = task.get('metadata', {}).get('contents', [])
    audio_urls = [
        {'audio_url': c.get('audio'), 'text': c.get('text', '')[:50]}
        for c in contents if c.get('audio')
    ]
    return {
        'summary': f"任务包含 {len(contents)} 条音频",
        'task_id': task.get('id'),
        'status': task.get('status'),
        'audio_urls': audio_urls,
        'merged_audio': task.get('metadata', {}).get('audio')
    }


@mcp.tool()
def delete_generation_task(task_id: str):
    """删除指定的异步生成任务"""
    result = client.delete_async_task(task_id)
    return {'summary': f"成功删除任务 {task_id}", 'message': result.get('message')}


@mcp.tool()
def get_account_info():
    """获取当前用户账户信息"""
    result = client.get_account_info()
    user = result.get('user', {})
    return {
        'summary': f"用户「{user.get('name')}」剩余 {user.get('credits')} 点数",
        'user_id': user.get('id'),
        'name': user.get('name'),
        'credits': user.get('credits'),
        'role': user.get('role')
    }


@mcp.tool()
def upload_voice_conversion_audio(audio_data_url: str):
    """上传音色转换所需音频"""
    result = client.upload_voice_conversion_audio(audio=audio_data_url)
    return {'summary': "成功上传音频", 'url': result.get('data', {}).get('url')}


@mcp.tool()
def create_voice_clone(name: str, prompt: str, model_version: str = 'v3.0',
                      language: str = 'auto', description: Optional[str] = None,
                      avatar: Optional[str] = None, vocal_filter: bool = False):
    """创建新的语音角色（语音克隆）"""
    result = client.create_voice(
        name=name, prompt=prompt, model_version=model_version,
        language=language, description=description, avatar=avatar, vocal_filter=vocal_filter
    )
    voice = result.get('data', {})
    return {
        'summary': f"成功创建语音角色「{voice.get('name')}」，状态: {voice.get('status')}",
        'voice_id': voice.get('id'),
        'status': voice.get('status')
    }


@mcp.tool()
def delete_voice(voice_id: str):
    """删除指定的语音角色"""
    result = client.delete_voice(voice_id)
    return {'summary': f"成功删除语音角色 {voice_id}", 'message': result.get('message')}


@mcp.tool()
def add_voice_style(voice_id: str, prompt: str, name: str,
                   description: Optional[str] = None, language: str = 'auto',
                   vocal_filter: bool = True):
    """为指定ID的语音角色添加新风格"""
    result = client.add_voice_style(
        voice_id=voice_id, prompt=prompt, name=name,
        description=description, language=language, vocal_filter=vocal_filter
    )
    style = result.get('data', {}).get('metadata', {}).get('prompts', [{}])[-1]
    return {'summary': f"成功添加风格「{style.get('name')}」", 'style_id': style.get('id')}


@mcp.tool()
def delete_voice_style(voice_id: str, prompt_id: str):
    """删除指定语音角色的指定风格"""
    result = client.delete_voice_style(voice_id, prompt_id)
    return {'summary': f"成功删除风格 {prompt_id}", 'message': result.get('message')}


@mcp.tool()
def get_voice_share_id(voice_id: str):
    """获取指定语音角色的一次性分享链接ID"""
    result = client.get_voice_share_id(voice_id)
    return {'summary': f"分享ID: {result.get('data', {}).get('shareId')}",
            'share_id': result.get('data', {}).get('shareId')}


@mcp.tool()
def add_voice_by_share(share_id: str):
    """通过分享ID将语音角色添加到账户中"""
    result = client.add_voice_by_share(share_id)
    voice = result.get('data', {})
    return {'summary': f"成功添加语音角色「{voice.get('name')}」",
            'voice_id': voice.get('id'), 'name': voice.get('name')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='悟声MCP服务器')
    parser.add_argument('port', nargs='?', type=int, default=PORT, help='监听端口')
    parser.add_argument('host', nargs='?', default=HOST, help='监听地址')
    args = parser.parse_args()

    print(f"=" * 60)
    print(f"悟声MCP服务器")
    print(f"=" * 60)
    print(f"API Key: {'已配置 ✓' if API_KEY else '未配置 ✗ (使用环境变量)'} ")
    print(f"服务器地址: http://{args.host}:{args.port}")
    print(f"SSE端点: http://{args.host}:{args.port}/sse")
    print(f"=" * 60)
    print(f"按 Ctrl+C 停止服务器")
    print(f"=" * 60)

    mcp.run(transport="sse", port=args.port, host=args.host)
