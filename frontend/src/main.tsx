import { createRoot } from 'react-dom/client';
import App from './app/App.tsx';
import './styles/index.css';

async function prepare() {
  if (import.meta.env.DEV) {
    const { worker } = await import('./mocks/browser');
    return worker.start({ onUnhandledRequest: 'bypass' });
  }
}

prepare().then(() => {
  createRoot(document.getElementById('root')!).render(<App />);
});
