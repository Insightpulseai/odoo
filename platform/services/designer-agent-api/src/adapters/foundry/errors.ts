export class DesignerAgentProviderError extends Error {
  readonly code = 'DESIGNER_AGENT_PROVIDER_ERROR';
}

export class DesignerAgentResponseParseError extends Error {
  readonly code = 'DESIGNER_AGENT_RESPONSE_PARSE_ERROR';
  readonly causeDetail?: unknown;

  constructor(message: string, causeDetail?: unknown) {
    super(message);
    this.causeDetail = causeDetail;
  }
}
