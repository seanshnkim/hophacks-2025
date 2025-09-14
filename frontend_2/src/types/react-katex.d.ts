declare module 'react-katex' {
  import { Component } from 'react';

  interface MathProps {
    math: string;
    errorColor?: string;
    renderError?: (error: any) => React.ReactNode;
  }

  export class InlineMath extends Component<MathProps> {}
  export class BlockMath extends Component<MathProps> {}
}
