import React, { useState } from 'react';

const LinearAlgebraForm = () => {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('beginner');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission logic here
    alert(`Topic: ${topic}, Difficulty: ${difficulty}`);
  };

  return (
    <form className="la-form" onSubmit={handleSubmit}>
      <h2>Linear Algebra Learning Materials</h2>
      <div>
        <label>
          Topic:
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. Matrix Multiplication"
            required
          />
        </label>
      </div>
      <div>
        <label>
          Difficulty:
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>
      </div>
      <button type="submit">Get Materials</button>
    </form>
  );
};

export default LinearAlgebraForm;