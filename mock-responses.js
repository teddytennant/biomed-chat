/**
 * Mock responses for Biomed Chat when XAI API key is not available
 * These responses simulate the streaming API format
 */

const mockResponses = [
  {
    trigger: ['ecg', 'ekg', 'electrocardiogram'],
    response: `**ECG Signal Analysis - Mock Response**

**Summary**: Standard ECG analysis involves signal preprocessing, feature extraction, and interpretation of cardiac rhythms.

**Steps**:
1. **Preprocessing**: Apply 0.5-50Hz bandpass filter to remove baseline drift and power line interference
2. **QRS Detection**: Use Pan-Tompkins algorithm or wavelet-based detection (sensitivity >99%)
3. **Feature Extraction**: Measure P-R interval (120-200ms), QRS width (<120ms), Q-T interval (<440ms corrected)
4. **Rhythm Analysis**: Calculate heart rate variability (HRV) and detect arrhythmias

**Key Params**:
- Sampling rate: ≥250 Hz (preferably 500-1000 Hz)
- Resolution: ≥12-bit ADC
- Lead placement: Standard 12-lead or modified configurations for specific applications

**Risks/Checks**:
- IEC 60601-2-25 compliance for cardiac monitors
- Motion artifact rejection algorithms
- Lead-off detection and patient safety isolation

**References**:
- Goldberger AL. Clinical Electrocardiography (8th ed)
- Pan-Tompkins QRS detection algorithm (IEEE Trans BME, 1985)`
  },
  {
    trigger: ['impedance', 'bioimpedance', 'eis'],
    response: `**Bioimpedance Measurement - Mock Response**

**Summary**: Bioimpedance spectroscopy measures tissue electrical properties for body composition, fluid status, or cellular analysis.

**Steps**:
1. **Electrode Configuration**: Choose 2-electrode (simple) or 4-electrode (tetrapolar) setup
2. **Frequency Selection**: Single frequency (50kHz) for body fat, multi-frequency (1kHz-1MHz) for detailed analysis
3. **Current Injection**: Apply safe AC current (10-800μA, IEC 60601 limits)
4. **Measurement**: Record magnitude and phase of voltage response

**Key Params**:
- Current amplitude: <1mA (safety limit)
- Frequency range: 1kHz-1MHz typical
- Electrode contact impedance: <5kΩ
- Resolution: 16-24 bit ADC for phase accuracy

**Risks/Checks**:
- Patient isolation per IEC 60601-1
- Skin preparation for consistent electrode contact
- Temperature compensation (0.2%/°C typical)
- Validate with known resistor standards

**References**:
- Grimnes & Martinsen. Bioimpedance and Bioelectricity Basics (3rd ed)
- Kyle et al. Bioelectrical impedance analysis (Am J Clin Nutr, 2004)`
  },
  {
    trigger: ['fda', '510k', 'regulatory'],
    response: `**FDA 510(k) Submission Process - Mock Response**

**Summary**: 510(k) demonstrates substantial equivalence to legally marketed predicate device through documented comparison.

**Steps**:
1. **Predicate Identification**: Find legally marketed device with same intended use and technological characteristics
2. **Risk Classification**: Confirm Class II device status and special controls requirements
3. **Performance Testing**: Conduct biocompatibility (ISO 10993), electrical safety (IEC 60601), and clinical performance studies
4. **Submission Preparation**: Compile device description, substantial equivalence comparison, and test data per 21 CFR 807.87

**Key Params**:
- Review timeline: 90 days (standard) + response time for additional information requests
- User fees: ~$12,745 (standard submitter, FY 2024)
- Predicate age: <10 years preferred, strong justification needed for older devices

**Risks/Checks**:
- Pre-submission meeting (Q-Sub) recommended for novel technologies
- ISO 13485 QMS implementation required before commercial distribution
- Labeling compliance per 21 CFR 801
- Post-market surveillance plan per 21 CFR 820.198

**References**:
- FDA Guidance: The 510(k) Program (July 2017)
- 21 CFR Part 807 - Establishment Registration and Device Listing`
  },
  {
    trigger: ['mri', 'magnetic resonance', 'imaging'],
    response: `**MRI Safety & Biomedical Engineering - Mock Response**

**Summary**: MRI systems require careful consideration of magnetic field interactions, RF heating, and patient safety protocols.

**Steps**:
1. **Zone Classification**: Implement 4-zone safety model (ACR guidelines)
2. **Device Testing**: Evaluate magnetic attraction, RF heating (SAR), and image artifacts per ASTM F2503
3. **Labeling**: Classify as MR Safe, MR Conditional, or MR Unsafe per ASTM F2503
4. **Installation**: Consider 5-gauss line, RF shielding, and helium quench vent systems

**Key Params**:
- Static field strength: 1.5T, 3T common clinical systems
- Gradient slew rate: <200 T/m/s typical safety limit
- SAR limits: 4 W/kg whole body (IEC 60601-2-33)
- Temperature rise: <1°C for passive implants

**Risks/Checks**:
- ASTM F2052 measurement of magnetically induced displacement force
- ASTM F2182 measurement of radio frequency induced heating
- Patient screening protocols per ACR MR Safe Practices
- Emergency procedures for ferromagnetic projectiles

**References**:
- ACR Guidance Document on MR Safe Practices (2020)
- IEC 60601-2-33: Medical electrical equipment - Part 2-33: Particular requirements for MR equipment`
  }
];

const generalMockResponse = `**Biomedical Engineering Consultation - Mock Response**

**Summary**: This is a simulated response from the Biomed Chat system operating in mock mode (no API key configured).

**Context**: 
The X.AI API key is not currently configured, so this system is providing mock responses for demonstration purposes. In production, you would receive AI-powered responses from Grok-4 tailored to biomedical engineering applications.

**To enable full functionality**:
1. Obtain an API key from X.AI (https://x.ai)
2. Add your key to the .env file: \`XAI_API_KEY=your_key_here\`
3. Restart the application

**Available Mock Topics**:
- ECG/EKG analysis and signal processing
- Bioimpedance measurements and applications
- FDA 510(k) regulatory pathways
- MRI safety and device compatibility

**Note**: These mock responses demonstrate the system's formatting and structure but lack the dynamic AI analysis you would receive with a configured API key.

**References**:
- This is mock data for testing purposes
- Real responses would include current literature and expert insights`;

function getMockResponse(userMessage) {
  const message = userMessage.toLowerCase();
  
  // Find matching mock response based on trigger words
  for (const mock of mockResponses) {
    if (mock.trigger.some(trigger => message.includes(trigger))) {
      return mock.response;
    }
  }
  
  // Return general mock response if no specific match found
  return generalMockResponse;
}

function createMockSSEStream(content) {
  const words = content.split(' ');
  let index = 0;
  let cancelled = false;
  
  return {
    cancel() {
      cancelled = true;
    },
    async* generate() {
      // Send initial chunk
      if (!cancelled) {
        yield `data: ${JSON.stringify({
          choices: [{
            delta: { content: "" }
          }]
        })}\n\n`;
      }
      
      // Send content word by word to simulate streaming
      while (index < words.length && !cancelled) {
        const chunk = index === 0 ? words[index] : ' ' + words[index];
        yield `data: ${JSON.stringify({
          choices: [{
            delta: { content: chunk }
          }]
        })}\n\n`;
        index++;
        
        // Add small delay to simulate realistic streaming
        await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100));
      }
      
      // Send completion signal
      if (!cancelled) {
        yield `data: [DONE]\n\n`;
      }
    }
  };
}

export { getMockResponse, createMockSSEStream };
