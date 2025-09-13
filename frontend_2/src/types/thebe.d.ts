declare global {
  interface Window {
    thebelab?: {
      bootstrap: (config?: any) => void;
    };
  }
}
