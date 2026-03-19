'use client';

import * as React from 'react';
import {
  FluentProvider,
  webLightTheme,
} from '@fluentui/react-components';

type Props = { children: React.ReactNode };

export function AppProviders({ children }: Props) {
  return (
    <FluentProvider theme={webLightTheme}>
      {children}
    </FluentProvider>
  );
}
