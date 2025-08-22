import React from 'react';
import './DnaSpinner.css';

const DnaSpinner = ({ size = 'medium' }) => {
  const sizeClasses = {
    small: 'scale-75',
    medium: 'scale-100',
    large: 'scale-125'
  };

  return (
    <div className={`dna-spinner ${sizeClasses[size]} pulse`}>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
      <div className="nucleobase"></div>
    </div>
  );
};

export default DnaSpinner;
