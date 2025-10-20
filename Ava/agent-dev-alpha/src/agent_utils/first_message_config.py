async def first_message_mode(session, config_data: dict):
    first_message_mode = config_data.get('firstMessageMode')
    first_message = config_data.get('firstMessage')
    
    # Execute first message behavior
    if first_message_mode != "assistant-waits-for-user":
        if first_message_mode == "assistant-speaks-first" and first_message:
            await session.say(first_message)
        else:
            await session.generate_reply(allow_interruptions=True)