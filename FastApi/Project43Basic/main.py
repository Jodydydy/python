from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from models import UserLogin, User, Content
from db import get_user, USERS_DATA, POSTS, resources
from dependencies import get_current_user
from security import create_jwt_token, username_from_request

from pyrate_limiter import Duration, Limiter, Rate

from fastapi_limiter.depends import RateLimiter

from rbacx import Guard, Subject, Action, Resource, Context
from rbacx.adapters.fastapi import require_access

from rbacx.policy.loader import FilePolicySource, HotReloader


app = FastAPI()

limiters = {'admin': RateLimiter(limiter=Limiter(Rate(1000, Duration.SECOND * 60))),
            'user': RateLimiter(limiter=Limiter(Rate(20, Duration.SECOND * 60))),
            'guest': RateLimiter(limiter=Limiter(Rate(5, Duration.SECOND * 60)))}

guard = Guard(policy={})
reloader = HotReloader(
    guard,
    FilePolicySource('policy.json'),
    initial_load=True
)

reloader.check_and_reload()

def make_env_builder(action_name:str, resource_type: str):
    def build_env(request: Request):
        username = username_from_request(request)
        user_obj = get_user(username)
        roles = user_obj.roles if user_obj else []
        subject = Subject(id=username, roles=roles)
        action = Action(action_name)
        resource = Resource(type=resource_type)
        context = Context()
        return subject, action, resource, context
    return build_env


def ownership_check(request: Request):
    username = username_from_request(request)
    username_path = request.path_params.get('username')
    user_obj = get_user(username)
    roles = user_obj.roles if user_obj else []
    resource = resources.get(username_path)

    if request.method != 'POST' and resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')

    if 'admin' in roles or username == username_path:
        return {username_path: resource}

    elif request.method == 'GET' and resource.get('is_public'):
        return {username_path: resource}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access to resource is blocked')    

            
    
async def get_rate_limit_by_role(request: Request, responce: Response):

    username = username_from_request(request)
    user_obj = get_user(username)
    roles = user_obj.roles if user_obj else []

    if 'admin' in roles:
        return await limiters.get('admin')(request, responce)
    elif 'user' in roles:
       return await limiters.get('user')(request, responce)
    elif 'guest' in roles:
       return await limiters.get('guest')(request, responce)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user')

@app.post('/login')
async def login(user: UserLogin):

    for u in USERS_DATA:
        if user.username == u['username'] and user.password == u['password']:
            token = create_jwt_token({'sub': user.username})
            return {'access_token': token, 'token_type': 'bearer'}
        
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authtorization') 



@app.post('/create', dependencies=[
    Depends(require_access(guard, make_env_builder('create', 'page'))),
    Depends(get_rate_limit_by_role)
])   
async def create_post(request: Request, post: dict, current_user: User = Depends(get_current_user)):

    POSTS.append(post)

    return {'message': 'Post added'}


@app.get('/read', dependencies=[
    Depends(require_access(guard, make_env_builder('read', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def read_post(post: dict, current_user: User = Depends(get_current_user)):

    for p in POSTS:
        print(p, post)
        if p.get('id') == post.get('id'):
            return {'message': p.get('message')}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')    


@app.put('/update', dependencies=[
    Depends(require_access(guard, make_env_builder('update', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def update_post(post: dict, current_user: User = Depends(get_current_user)):

    for p in POSTS:
        if p.get('id') == post.get('id'):
            p['message'] = post['message']
            return {'message': 'Post updated'}        

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')    

@app.delete('/delete', dependencies=[
    Depends(require_access(guard, make_env_builder('delete', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def delete_post(post: dict, current_user: User = Depends(get_current_user)):

    for p in POSTS:
        if p.get('id') == post.get('id'):
            POSTS.remove(p)
            return {'message': 'Post deleted'}        

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')    


@app.get('/protected_resource/{username}', dependencies=[
    Depends(require_access(guard, make_env_builder('protected_read', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def protected_resource_get(username: str, resource: dict = Depends(ownership_check), current_user: User = Depends(get_current_user)):

    content = resources[username].get('content') 
    return {'message': f'Welcome {current_user.username}. Resource: {content}'}


@app.post('/protected_resource/{username}', dependencies=[
    Depends(require_access(guard, make_env_builder('protected_post', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def protected_resource_post(username: str, content: Content, resource: dict = Depends(ownership_check), current_user: User = Depends(get_current_user)):

    resources.update({username: content.model_dump()})
    return {'message': f'Welcome {current_user.username}. Resource added'}


@app.put('/protected_resource/{username}', dependencies=[
    Depends(require_access(guard, make_env_builder('protected_put', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def protected_resource_put(username: str, content: Content, resource: dict = Depends(ownership_check), current_user: User = Depends(get_current_user)):
    resources[username] = content.model_dump()
    return {'message': f'Welcome {current_user.username}. Resource updated'}


@app.delete('/protected_resource/{username}', dependencies=[
    Depends(require_access(guard, make_env_builder('protected_delete', 'page'))),
    Depends(get_rate_limit_by_role)
])
async def protected_resource_delete(username: str, resource: dict = Depends(ownership_check), current_user: User = Depends(get_current_user)):
    del resources[username]
    return {'message': f'Welcome {current_user.username}. Resource deleted'}