VALID_CHAT_ROLES = ["developer", "system", "user", "assistant"]


async def setup_agent_context(session, config_data: dict):
    chat_ctx = session.chat_ctx.copy()
    
    for message in config_data['model']['messages']:
        role = message.get('role')
        content = message.get('content')  
        if role in VALID_CHAT_ROLES and content and isinstance(content, str):
            chat_ctx.add_message(role=role, content=content)
    await session.update_chat_ctx(chat_ctx)