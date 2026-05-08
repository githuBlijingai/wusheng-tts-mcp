import os
import httpx
from typing import Optional, List, Dict, Any
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

API_BASE_URL = os.getenv('WUSOUND_API_BASE_URL', 'https://v1.wusound.cn')
HOST = os.getenv('API_HOST', '0.0.0.0')
PORT = int(os.getenv('API_PORT', '8000'))

app = FastAPI(title="悟声语音合成API", version="1.0")


class WuSoundClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = API_BASE_URL

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        url = f"{self.base_url}{endpoint}"
        with httpx.Client(timeout=60.0) as client:
            response = client.request(method, url, headers=headers, **kwargs)
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
                    avatar: Optional[str] = None, vocal_filter: bool = False) -> Dict[str, Any]:
        data = {
            'name': name, 'prompt': prompt, 'modelVersion': model_version,
            'language': language, 'vocalFilter': vocal_filter
        }
        if description:
            data['description'] = description
        if avatar:
            data['avatar'] = avatar
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


@app.get("/")
async def root():
    return {
        "service": "悟声语音合成API",
        "version": "1.0",
        "docs": "/docs",
        "endpoints": [
            "GET /account/info - 获取账户信息",
            "GET /voices - 获取角色列表",
            "GET /voices/{id} - 获取角色详情",
            "POST /voices - 创建角色",
            "DELETE /voices/{id} - 删除角色",
            "POST /voices/{id}/style - 添加风格",
            "DELETE /voices/{id}/style/{style_id} - 删除风格",
            "POST /generate/speech - 生成语音",
            "POST /generate/async - 异步生成",
            "GET /generate/tasks - 获取任务列表",
            "GET /generate/tasks/{id} - 获取任务详情",
            "DELETE /generate/tasks/{id} - 删除任务"
        ]
    }


@app.get("/account/info")
async def get_account_info(authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.get_account_info()
    user = result.get('user', {})
    return {
        'summary': f"用户「{user.get('name')}」剩余 {user.get('credits')} 点数",
        'user_id': user.get('id'),
        'name': user.get('name'),
        'credits': user.get('credits'),
        'role': user.get('role')
    }


@app.get("/voices")
async def get_voices(authorization: str = Header(...), from_type: str = None, show_market: bool = False):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
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
                'description': v.get('metadata', {}).get('description', '')
            }
            for v in voices
        ]
    }


@app.get("/voices/{voice_id}")
async def get_voice_detail(voice_id: str, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
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


class CreateVoiceRequest(BaseModel):
    name: str
    prompt: str
    model_version: str = 'v3.0'
    language: str = 'auto'
    description: Optional[str] = None
    avatar: Optional[str] = None
    vocal_filter: bool = False


@app.post("/voices")
async def create_voice(request: CreateVoiceRequest, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.create_voice(
        name=request.name, prompt=request.prompt, model_version=request.model_version,
        language=request.language, description=request.description,
        avatar=request.avatar, vocal_filter=request.vocal_filter
    )
    voice = result.get('data', {})
    return {
        'summary': f"成功创建语音角色「{voice.get('name')}」",
        'voice_id': voice.get('id'),
        'status': voice.get('status')
    }


@app.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.delete_voice(voice_id)
    return {'summary': f"成功删除语音角色", 'message': result.get('message')}


class AddStyleRequest(BaseModel):
    prompt: str
    name: str
    description: Optional[str] = None
    language: str = 'auto'
    vocal_filter: bool = True


@app.post("/voices/{voice_id}/style")
async def add_voice_style(voice_id: str, request: AddStyleRequest, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.add_voice_style(
        voice_id=voice_id, prompt=request.prompt, name=request.name,
        description=request.description, language=request.language, vocal_filter=request.vocal_filter
    )
    style = result.get('data', {}).get('metadata', {}).get('prompts', [{}])[-1]
    return {'summary': f"成功添加风格「{style.get('name')}」", 'style_id': style.get('id')}


@app.delete("/voices/{voice_id}/style/{style_id}")
async def delete_voice_style(voice_id: str, style_id: str, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.delete_voice_style(voice_id, style_id)
    return {'summary': f"成功删除风格", 'message': result.get('message')}


class GenerateSpeechRequest(BaseModel):
    voice_id: str
    text: str
    prompt_id: str = 'default'
    preset: str = 'balance'
    language: str = 'auto'
    speech_rate: float = 1.0


@app.post("/generate/speech")
async def generate_speech(request: GenerateSpeechRequest, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.simple_generate(
        voice_id=request.voice_id, text=request.text, prompt_id=request.prompt_id,
        preset=request.preset, language=request.language, speech_rate=request.speech_rate
    )
    data = result.get('data', {})
    return {
        'summary': f"成功生成音频，消耗 {data.get('credit_used', 0)} 点数",
        'audio_url': data.get('audio'),
        'stream_url': data.get('streamUrl'),
        'credit_used': data.get('credit_used')
    }


class AsyncContent(BaseModel):
    voice_id: str
    text: str
    prompt_id: str = 'default'
    preset: str = 'balance'
    language: str = 'auto'
    speech_rate: float = 1.0


class CreateAsyncRequest(BaseModel):
    contents: List[AsyncContent]
    srt: bool = False


@app.post("/generate/async")
async def create_async_generation(request: CreateAsyncRequest, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    formatted_contents = [
        {
            'voiceId': c.voice_id,
            'text': c.text,
            'promptId': c.prompt_id,
            'preset': c.preset,
            'language': c.language,
            'speechRate': c.speech_rate
        }
        for c in request.contents
    ]
    result = client.create_async_generation(contents=formatted_contents, srt=request.srt)
    task = result.get('data', {})
    return {
        'summary': f"成功创建异步生成任务",
        'task_id': task.get('id'),
        'status': task.get('status')
    }


@app.get("/generate/tasks")
async def get_generation_tasks(
    authorization: str = Header(...),
    limit: int = 20,
    offset: int = 0,
    status: str = None
):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.get_async_tasks(limit=limit, offset=offset, status=status)
    tasks = result.get('data', [])
    return {
        'summary': f"共找到 {len(tasks)} 个任务",
        'tasks': [
            {'id': t.get('id'), 'status': t.get('status'),
             'characters': t.get('metadata', {}).get('characters', 0)}
            for t in tasks
        ]
    }


@app.get("/generate/tasks/{task_id}")
async def get_generation_task_detail(task_id: str, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.get_async_task_detail(task_id)
    task = result.get('data', {})
    contents = task.get('metadata', {}).get('contents', [])
    return {
        'summary': f"任务包含 {len(contents)} 条音频",
        'task_id': task.get('id'),
        'status': task.get('status'),
        'merged_audio': task.get('metadata', {}).get('audio')
    }


@app.delete("/generate/tasks/{task_id}")
async def delete_generation_task(task_id: str, authorization: str = Header(...)):
    api_key = authorization.replace('Bearer ', '')
    client = WuSoundClient(api_key)
    result = client.delete_async_task(task_id)
    return {'summary': f"成功删除任务", 'message': result.get('message')}


if __name__ == '__main__':
    print(f"=" * 60)
    print(f"悟声语音合成 REST API 服务器")
    print(f"=" * 60)
    print(f"API文档: http://{HOST}:{PORT}/docs")
    print(f"服务器地址: http://{HOST}:{PORT}")
    print(f"=" * 60)
    uvicorn.run(app, host=HOST, port=PORT)
