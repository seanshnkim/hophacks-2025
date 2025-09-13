import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Linear Algebra Learning Materials form', () => {
  render(<App />);
  const titleElement = screen.getByText(/Linear Algebra Learning Materials/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders topic input field', () => {
  render(<App />);
  const topicInput = screen.getByLabelText(/Topic:/i);
  expect(topicInput).toBeInTheDocument();
});

test('renders difficulty select field', () => {
  render(<App />);
  const difficultySelect = screen.getByLabelText(/Difficulty:/i);
  expect(difficultySelect).toBeInTheDocument();
});

test('renders get materials button', () => {
  render(<App />);
  const button = screen.getByRole('button', { name: /Get Materials/i });
  expect(button).toBeInTheDocument();
});
