from typing import Dict, Any
from agent_utils.model_providers import ProviderMappings


def extract_provider_instance(config: Dict[str, Any], provider_type: str):
    provider_name = config['provider'].lower()
    
    if provider_type == 'llm':
        params = {'model': config['model']}
        for key, value in config.items():
            if key not in ['provider', 'model'] and value is not None:
                params[key] = value
    else:
        params = {key: value for key, value in config.items() if key != 'provider'}

    if 'with_' in provider_name and '_openai' in provider_name:
        dynamic_method = provider_name.replace('with_', '').replace('_openai', '')
        openai_provider = ProviderMappings.get_openai_provider()
        return getattr(getattr(openai_provider, provider_type.upper()), f'with_{dynamic_method}')(**params)
    else:
        provider = ProviderMappings.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Unsupported {provider_type.upper()} provider: {provider_name}")
        return getattr(provider, provider_type.upper())(**params)


def create_provider_instances(metadata: Dict[str, Any]) -> Dict[str, Any]:
    llm_config = {k: v for k, v in metadata['model'].items() if k not in ['messages', 'toolIds']}
    tts_config = metadata['voice']
    stt_config = metadata['transcriber']
    
    return {
        'llm': extract_provider_instance(llm_config, 'llm'),
        'tts': extract_provider_instance(tts_config, 'tts'),
        'stt': extract_provider_instance(stt_config, 'stt')
    }