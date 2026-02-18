import type { StatusResponse } from '../../../tools/colima-desktop/src/shared/contracts/status';
import type { LifecycleResponse } from '../../../tools/colima-desktop/src/shared/contracts/lifecycle';

declare global {
  interface Window {
    colima: {
      status(): Promise<StatusResponse>;
      start(): Promise<LifecycleResponse>;
      stop(): Promise<LifecycleResponse>;
      restart(): Promise<LifecycleResponse>;
    };
  }
}

export {};
