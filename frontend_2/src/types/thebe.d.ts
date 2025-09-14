declare global {
  interface Window {
    thebe?: {
      init: (config?: any) => any;
      createNotebook: (element: HTMLElement) => any;
    };
    thebelab?: {
      bootstrap: (config?: any) => void;
    };
  }
}
