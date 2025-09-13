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
      <div className="la-form-header">
        <img src="https://img.icons8.com/fluency/48/000000/matrix.png" alt="Matrix Icon" className="la-form-icon" />
        <h2>Linear Algebra Learning Materials</h2>
        <p className="la-form-desc">Find resources tailored to your topic and skill level.</p>
      </div>
      <div className="la-form-group">
        <label htmlFor="topic">Topic</label>
        <input
          id="topic"
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Matrix Multiplication"
          required
        />
      </div>
      <div className="la-form-group">
        <label htmlFor="difficulty">Difficulty</label>
        <select
          id="difficulty"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>
      <button className="la-form-btn" type="submit">Get Materials</button>
    </form>
  );
};

export default LinearAlgebraForm;
