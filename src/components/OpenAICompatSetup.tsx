import React, { useState } from 'react';
import { Box, Text } from '../ink.js';
import TextInput from './TextInput.js';
import { Select } from './CustomSelect/select.js';
import { saveGlobalConfig } from '../utils/config.js';
import { useTerminalSize } from '../hooks/useTerminalSize.js';
import { useInput } from '../ink.js';

type SetupStep = 'provider' | 'api_key' | 'model' | 'custom_url';

const PROVIDER_PRESETS = [
  {
    label: <Text>优云智算 · <Text dimColor>https://api.modelverse.cn/v1</Text>{"\n"}</Text>,
    value: 'modelverse',
  },
  {
    label: <Text>DeepSeek · <Text dimColor>https://api.deepseek.com</Text>{"\n"}</Text>,
    value: 'deepseek',
  },
  {
    label: <Text>Ollama (local) · <Text dimColor>http://localhost:11434</Text>{"\n"}</Text>,
    value: 'ollama',
  },
  {
    label: <Text>Custom URL · <Text dimColor>Enter API address manually</Text>{"\n"}</Text>,
    value: 'custom',
  },
];

const PRESET_CONFIGS: Record<string, { baseUrl: string; needsKey: boolean }> = {
  modelverse: { baseUrl: 'https://api.modelverse.cn/v1', needsKey: true },
  deepseek: { baseUrl: 'https://api.deepseek.com', needsKey: true },
  ollama: { baseUrl: 'http://localhost:11434', needsKey: false },
  custom: { baseUrl: '', needsKey: true },
};

type Props = {
  onDone: () => void;
  onBack: () => void;
};

const INPUT_PROMPT = '> ';

function StepInput({ label, hint, mask, onSubmit, dimExamples }: {
  label: React.ReactNode;
  hint?: string;
  mask?: string;
  onSubmit: (val: string) => void;
  dimExamples?: string;
}): React.ReactNode {
  const [value, setValue] = useState('');
  const [cursorOffset, setCursorOffset] = useState(0);
  const columns = useTerminalSize().columns - INPUT_PROMPT.length - 1;

  // Listen for Enter key directly
  useInput((_input: string, key: any) => {
    if (key.return) {
      onSubmit(value);
    }
  });

  return (
    <Box flexDirection="column" gap={1}>
      {label}
      <Box>
        <Text>{INPUT_PROMPT}</Text>
        <TextInput
          value={value}
          onChange={setValue}
          cursorOffset={cursorOffset}
          onChangeCursorOffset={setCursorOffset}
          columns={columns}
          mask={mask}
        />
      </Box>
      {dimExamples && <Text dimColor>{dimExamples}</Text>}
    </Box>
  );
}

export function OpenAICompatSetup({ onDone, onBack }: Props): React.ReactNode {
  const [step, setStep] = useState<SetupStep>('provider');
  const [baseUrl, setBaseUrl] = useState('');
  const [apiKey, setApiKey] = useState('');

  function applyConfig(finalBaseUrl: string, finalApiKey: string, finalModel: string) {
    process.env.CLAUDE_CODE_USE_OPENAI_COMPAT = '1';
    process.env.OPENAI_COMPAT_BASE_URL = finalBaseUrl;
    process.env.OPENAI_COMPAT_API_KEY = finalApiKey;
    process.env.OPENAI_COMPAT_MODEL = finalModel;

    saveGlobalConfig(current => ({
      ...current,
      openaiCompat: {
        baseUrl: finalBaseUrl,
        apiKey: finalApiKey,
        model: finalModel,
      },
      hasCompletedOnboarding: true,
    }));

    onDone();
  }

  if (step === 'provider') {
    return (
      <Box flexDirection="column" gap={1} marginTop={1}>
        <Text bold>Configure OpenAI-compatible API</Text>
        <Text dimColor>Supports any API compatible with OpenAI chat completions format.</Text>
        <Text>Select a provider:</Text>
        <Box>
          <Select
            options={PROVIDER_PRESETS}
            onChange={(value: string) => {
              const preset = PRESET_CONFIGS[value];
              if (!preset) return;
              setBaseUrl(preset.baseUrl);
              if (value === 'custom') {
                setStep('custom_url');
              } else if (!preset.needsKey) {
                setStep('model');
              } else {
                setStep('api_key');
              }
            }}
          />
        </Box>
      </Box>
    );
  }

  if (step === 'custom_url') {
    return (
      <Box flexDirection="column" gap={1} marginTop={1}>
        <Text bold>Configure OpenAI-compatible API</Text>
        <StepInput
          label={<Text>Enter API Base URL:</Text>}
          dimExamples="Examples: https://api.deepseek.com | https://api.modelverse.cn/v1"
          onSubmit={(val) => {
            setBaseUrl(val.trim() || 'http://localhost:11434');
            setStep('api_key');
          }}
        />
      </Box>
    );
  }

  if (step === 'api_key') {
    return (
      <Box flexDirection="column" gap={1} marginTop={1}>
        <Text bold>Configure OpenAI-compatible API</Text>
        <Text color="green">✓ URL: {baseUrl}</Text>
        <StepInput
          label={<Text>Enter API Key <Text dimColor>(press Enter to skip)</Text>:</Text>}
          mask="*"
          onSubmit={(val) => {
            setApiKey(val.trim());
            setStep('model');
          }}
        />
      </Box>
    );
  }

  if (step === 'model') {
    return (
      <Box flexDirection="column" gap={1} marginTop={1}>
        <Text bold>Configure OpenAI-compatible API</Text>
        <Text color="green">✓ URL: {baseUrl}</Text>
        <Text color="green">✓ Key: {apiKey ? '****' + apiKey.slice(-4) : '(none)'}</Text>
        <StepInput
          label={<Text>Enter Model name:</Text>}
          dimExamples="Examples: deepseek-chat | deepseek-reasoner | qwq-32b | MiniMax-M2.5"
          onSubmit={(val) => {
            const finalModel = val.trim();
            if (!finalModel) return;
            applyConfig(baseUrl, apiKey, finalModel);
          }}
        />
      </Box>
    );
  }

  return null;
}
