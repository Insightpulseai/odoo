import { useState } from 'react';
import {
  makeStyles,
  tokens,
  Text,
  Card,
  Input,
  Button,
  Badge,
  Divider,
} from '@fluentui/react-components';
import {
  DismissRegular,
  SendRegular,
  BotRegular,
  PersonRegular,
} from '@fluentui/react-icons';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    borderLeft: `1px solid ${tokens.colorNeutralStroke1}`,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: tokens.spacingHorizontalM,
    borderBottom: `1px solid ${tokens.colorNeutralStroke1}`,
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  messages: {
    flex: 1,
    overflow: 'auto',
    padding: tokens.spacingHorizontalM,
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalS,
  },
  message: {
    padding: tokens.spacingVerticalS,
  },
  messageHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalXS,
    marginBottom: tokens.spacingVerticalXS,
  },
  inputArea: {
    display: 'flex',
    gap: tokens.spacingHorizontalS,
    padding: tokens.spacingHorizontalM,
    borderTop: `1px solid ${tokens.colorNeutralStroke1}`,
  },
});

interface CopilotPanelProps {
  onClose: () => void;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  mode?: string;
}

const initialMessages: Message[] = [
  {
    role: 'assistant',
    content: 'Hello! I\'m Diva Copilot in Strategy mode. I can help you review goal status, check evidence, or assess capability gaps. What would you like to know?',
    mode: 'Strategy',
  },
];

export function CopilotPanel({ onClose }: CopilotPanelProps) {
  const styles = useStyles();
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: input },
      {
        role: 'assistant',
        content: `Based on the evidence from Odoo and Databricks, I can see that this goal is tracking at 82% confidence. The key risk area is the ipai_diva module development timeline. [kb_strategy, kb_execution]`,
        mode: 'Strategy',
      },
    ]);
    setInput('');
  };

  return (
    <div className={styles.root}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <BotRegular fontSize={20} />
          <Text weight="semibold">Diva Copilot</Text>
          <Badge color="brand" appearance="outline" size="small">Strategy</Badge>
        </div>
        <Button
          icon={<DismissRegular />}
          appearance="subtle"
          size="small"
          onClick={onClose}
        />
      </div>
      <div className={styles.messages}>
        {messages.map((msg, i) => (
          <Card key={i} className={styles.message} size="small">
            <div className={styles.messageHeader}>
              {msg.role === 'assistant' ? <BotRegular fontSize={16} /> : <PersonRegular fontSize={16} />}
              <Text size={200} weight="semibold">
                {msg.role === 'assistant' ? 'Diva Copilot' : 'You'}
              </Text>
              {msg.mode && (
                <Badge color="brand" appearance="outline" size="tiny">{msg.mode}</Badge>
              )}
            </div>
            <Text size={300}>{msg.content}</Text>
          </Card>
        ))}
      </div>
      <Divider />
      <div className={styles.inputArea}>
        <Input
          placeholder="Ask about goals, evidence, capabilities..."
          value={input}
          onChange={(_, data) => setInput(data.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          style={{ flex: 1 }}
        />
        <Button icon={<SendRegular />} appearance="primary" onClick={handleSend} />
      </div>
    </div>
  );
}
