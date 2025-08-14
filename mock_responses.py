# mock_responses.py
"""
Mock response system for demo mode when API key is not available.
Provides realistic biomedical engineering responses for common queries.
"""

import random
import time
import json
from typing import Dict, List, Any
from datetime import datetime

class MockResponseGenerator:
    """Generate realistic mock responses for biomedical queries."""
    
    def __init__(self):
        self.response_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load response templates for various biomedical topics."""
        return {
            "crispr": [
                """CRISPR-Cas9 represents a revolutionary gene-editing technology that has transformed biomedical research and therapeutic development.

**Key Technical Aspects:**
• **Mechanism**: Uses guide RNA (gRNA) to direct Cas9 endonuclease to specific genomic loci
• **Efficiency**: Typically achieves 60-80% editing efficiency in optimized conditions
• **Off-target effects**: Modern variants (SpCas9-HF1, eSpCas9) reduce off-target activity by >95%

**Current Applications in Biomedicine:**
1. **Therapeutic Development**: CAR-T cell engineering, sickle cell disease treatment (CTX001)
2. **Disease Modeling**: Creating isogenic cell lines for drug screening
3. **Diagnostic Tools**: SHERLOCK/DETECTR platforms for pathogen detection

**Recent Advances (2024):**
- Prime editing 3 (PE3) achieving up to 20% efficiency without DSBs
- Base editors (ABE8e, TadA-V106W) with >80% editing efficiency
- Epigenome editors for reversible gene regulation

**Regulatory Considerations:**
The FDA requires comprehensive off-target analysis via GUIDE-seq or CIRCLE-seq for IND applications. Current clinical trials must demonstrate <0.1% off-target editing in therapeutically relevant sites.""",
                
                """CRISPR technology has evolved significantly beyond the original Cas9 system, offering biomedical engineers powerful tools for genetic manipulation.

**Technical Specifications:**
• PAM Requirements: NGG for SpCas9, NNGRRT for SaCas9, TTTV for Cas12a
• Delivery Methods: AAV (4.7kb limit), LNP (>95% hepatocyte targeting), ex vivo electroporation
• Editing Window: Typically 3-8bp upstream of PAM for base editors

**Biomedical Engineering Applications:**
- **Cell Line Development**: Knock-in/knock-out efficiency >70% using HDR templates
- **Organoid Engineering**: Creating disease models with patient-specific mutations
- **Biosensor Development**: CRISPR-based detection achieving attomolar sensitivity

**Quality Control Metrics:**
- Indel frequency analysis via NGS (requirement: >10,000x coverage)
- TIDE analysis for quick screening (limitation: <20% reference sequence)
- ddPCR for precise quantification (detection limit: 0.1% edited alleles)

**Manufacturing Considerations:**
GMP-grade Cas9 protein: $2,000-5,000/mg, gRNA synthesis: $0.15-0.30/base at scale. Consider using ribonucleoprotein (RNP) delivery for reduced immunogenicity in clinical applications."""
            ],
            
            "ecg": [
                """ECG signal processing requires sophisticated algorithms for accurate cardiac event detection and classification in biomedical devices.

**Signal Acquisition Parameters:**
• **Sampling Rate**: Minimum 500 Hz (AHA recommendation), 1000 Hz for high-frequency components
• **Resolution**: 12-16 bits, LSB ≤ 5μV for diagnostic quality
• **Bandwidth**: 0.05-150 Hz for diagnostic ECG, 0.5-50 Hz for monitoring

**QRS Detection Algorithms:**
1. **Pan-Tompkins**: Sensitivity 99.3%, PPV 99.5% on MIT-BIH database
2. **Wavelet Transform**: Better noise immunity, 15-20ms detection delay
3. **Deep Learning**: CNN-LSTM achieving 99.8% accuracy (requires 50k+ training samples)

**Noise Mitigation Strategies:**
- **Baseline Wander**: Butterworth HPF at 0.5 Hz or cubic spline interpolation
- **Powerline Interference**: Adaptive notch filter or regression subtraction
- **Motion Artifacts**: Adaptive filtering with accelerometer reference

**IEC 60601-2-27 Compliance:**
- Common-mode rejection: >89 dB at 50/60 Hz
- Input impedance: >10 MΩ at 10 Hz
- Patient leakage current: <10 μA (normal), <50 μA (single fault)

**Real-time Processing Requirements:**
Latency <200ms for arrhythmia detection, <40ms for pacemaker applications.""",
                
                """Advanced ECG analysis for biomedical applications involves multi-lead interpretation and automated diagnostic algorithms.

**12-Lead ECG Analysis Pipeline:**
• Lead Configuration: Standard (I, II, III, aVR, aVL, aVF, V1-V6) + derived leads (V7-V9)
• Preprocessing: Median filter (5-7 samples) → Butterworth bandpass → Baseline correction
• Feature Extraction: 150+ morphological and temporal features per heartbeat

**Heart Rate Variability (HRV) Metrics:**
- **Time Domain**: SDNN >100ms (normal), RMSSD for parasympathetic tone
- **Frequency Domain**: LF/HF ratio 1.5-2.0 (balanced autonomic activity)
- **Nonlinear**: Sample entropy 1.0-1.5, DFA α1 ~1.0 for healthy subjects

**Arrhythmia Detection Performance:**
- Atrial Fibrillation: Sensitivity 97%, Specificity 99% using RR interval analysis
- Ventricular Tachycardia: Detection within 2.5 seconds per AHA guidelines
- ST-Elevation: ≥0.1mV elevation, measured 60-80ms after J-point

**FDA 510(k) Submission Requirements:**
- Clinical validation: Minimum 150 patients, diverse demographics
- Performance testing per IEC 60601-2-25
- Software validation per IEC 62304 (Class B or C)
- Cybersecurity assessment per FDA guidance

**Implementation Considerations:**
Processing load: ~5 MFLOPS per channel at 1kHz. Consider DSP or FPGA for battery-powered devices."""
            ],
            
            "drug_design": [
                """Computational drug design in biomedical engineering leverages molecular modeling and AI for therapeutic development.

**Molecular Property Optimization:**
• **Lipinski's Rule of Five**: MW <500 Da, LogP <5, HBD ≤5, HBA ≤10
• **Veber's Rules**: Rotatable bonds ≤10, TPSA ≤140 Ų
• **QED Score**: >0.5 for drug-like properties (industry standard)

**ADMET Prediction Models:**
- **Absorption**: Caco-2 permeability >10^-5 cm/s for oral bioavailability
- **Distribution**: Vd 0.7-2.0 L/kg for ideal tissue distribution
- **Metabolism**: CYP450 interaction screening (3A4, 2D6, 2C9 primary)
- **Excretion**: CLtotal 5-15 mL/min/kg for optimal half-life

**Structure-Based Drug Design:**
1. **Molecular Docking**: Glide XP achieving <2Å RMSD in 78% of cases
2. **MD Simulations**: 100-500ns for binding stability assessment
3. **Free Energy Calculations**: FEP+ with <1 kcal/mol error for analogs

**AI/ML Applications:**
- Graph Neural Networks: R² >0.85 for property prediction
- Generative Models: VAE/GAN producing 60% synthesizable molecules
- Active Learning: 5-10x reduction in required experimental validations

**Development Pipeline Metrics:**
Hit-to-lead: 1:1000 success rate, Lead optimization: 6-18 months, IND-enabling studies: $2-5M investment.""",
                
                """Modern drug development integrates bioengineering principles for targeted therapeutic delivery and enhanced efficacy.

**Nanoparticle Drug Delivery Systems:**
• Size Range: 50-200nm for EPR effect exploitation
• Zeta Potential: -10 to +10mV for reduced opsonization
• PDI: <0.3 for uniform distribution
• Encapsulation Efficiency: >70% for cost-effectiveness

**Pharmacokinetic Modeling:**
- **One-Compartment**: IV bolus, first-order elimination (ke = 0.693/t½)
- **Two-Compartment**: Distribution phase (α) and elimination phase (β)
- **PBPK Models**: 14+ compartments, requires 50+ physiological parameters
- **Population PK**: NONMEM achieving <20% prediction error

**Formulation Development:**
1. **Immediate Release**: Dissolution >85% in 30 minutes (BCS Class I)
2. **Sustained Release**: Zero-order kinetics via osmotic pumps
3. **Targeted Delivery**: Antibody conjugation (DAR 2-4 optimal)

**Regulatory Bioequivalence:**
- AUC ratio: 80-125% (90% CI)
- Cmax ratio: 80-125% (90% CI)
- Tmax: No statistical requirement for IR formulations

**Quality by Design (QbD):**
Critical Quality Attributes (CQAs), Design Space definition per ICH Q8, Control Strategy with PAT implementation."""
            ],
            
            "imaging": [
                """Medical imaging processing for biomedical applications requires understanding of acquisition physics and reconstruction algorithms.

**MRI Technical Parameters:**
• **Field Strength**: 1.5T (clinical standard), 3T (research), 7T+ (ultra-high field)
• **Gradient Performance**: 40-80 mT/m strength, 200 T/m/s slew rate
• **SAR Limits**: Whole body <4 W/kg, head <3.2 W/kg, local <10 W/kg

**Image Reconstruction Algorithms:**
1. **Parallel Imaging**: SENSE/GRAPPA with R=2-4 acceleration
2. **Compressed Sensing**: 4-8x acceleration with <5% error
3. **Deep Learning**: Unrolled networks achieving 10x acceleration

**Segmentation Performance Metrics:**
- Dice Coefficient: >0.85 for clinical acceptance
- Hausdorff Distance: <5mm for boundary accuracy
- Volume Error: <10% for treatment planning

**DICOM Standards Compliance:**
- Modality-specific tags (0008,0060)
- Patient orientation (0020,0037)
- Window center/width optimization
- GSPS for annotation storage

**FDA Clearance Considerations:**
- 510(k) for substantially equivalent devices
- De Novo for novel imaging biomarkers
- Clinical validation: 100+ cases with ground truth
- Reader studies: 3+ radiologists, ICC >0.8"""
            ],
            
            "biomaterials": [
                """Biomaterial selection and characterization for medical device applications requires comprehensive biocompatibility assessment.

**Material Properties Requirements:**
• **Mechanical**: E-modulus matching tissue (bone: 10-30 GPa, soft tissue: 0.1-1 MPa)
• **Surface**: Contact angle 40-60° for optimal cell adhesion
• **Degradation**: 0.1-1% mass loss/month for resorbable implants

**Biocompatibility Testing (ISO 10993):**
1. **Cytotoxicity**: L929 fibroblast viability >70% (ISO 10993-5)
2. **Sensitization**: Guinea pig maximization test (ISO 10993-10)
3. **Hemocompatibility**: Hemolysis <5%, platelet adhesion <20% reduction
4. **Genotoxicity**: Ames test, chromosome aberration (ISO 10993-3)

**Surface Modification Techniques:**
- **Plasma Treatment**: Increases hydrophilicity, 20-50% improved cell adhesion
- **Protein Coating**: RGD peptides at 10-100 μg/cm² density
- **Drug Elution**: First-order release, 80% in 28 days for DES

**Sterilization Validation:**
- Gamma: 25-40 kGy dose, material property changes <10%
- EtO: 600 mg/L, 4-hour exposure, <250 ppm residual
- Steam: 121°C/15 min or 134°C/3 min, moisture-sensitive materials excluded

**Manufacturing Controls:**
GMP Class 7 cleanroom (10,000 particles/m³), endotoxin <0.5 EU/mL for implants."""
            ],
            
            "regulatory": [
                """FDA regulatory pathway navigation for biomedical devices requires strategic planning and comprehensive documentation.

**510(k) Submission Requirements:**
• **Substantial Equivalence**: Same intended use, similar technological characteristics
• **Performance Testing**: Bench, animal, and/or clinical data
• **Timeline**: 90-day FDA review (70% cleared in first round)
• **Cost**: FDA fee $19,870 (FY2024), total preparation $50-250k

**Design Controls (21 CFR 820.30):**
1. **Design Planning**: Define deliverables, responsibilities, interfaces
2. **Design Input**: User needs → design requirements traceability
3. **Design Output**: Specifications meeting design input
4. **Design Verification**: Testing to confirm output meets input
5. **Design Validation**: Clinical use simulation, 95/95 confidence

**Clinical Trial Requirements:**
- **IDE Application**: Required for significant risk devices
- **Sample Size**: Power >80%, α=0.05, clinically meaningful difference
- **GCP Compliance**: ICH E6, monitoring plan, SAE reporting <24 hours
- **Endpoints**: Primary (safety/efficacy), secondary, exploratory

**Quality System Regulation (QSR):**
- CAPA system with trending analysis
- Document control per 21 CFR 820.40
- Supplier controls with critical component identification
- Annual management review with quality metrics

**Post-Market Requirements:**
MDR reporting, annual registration, periodic 510(k) updates for modifications."""
            ],
            
            "general": [
                """I'm running in demo mode to showcase the biomedical engineering chatbot capabilities. While I don't have access to the full AI model right now, I can demonstrate how the system works with relevant biomedical engineering topics.

**Available Demo Topics:**
• CRISPR and gene editing technologies
• ECG/cardiac signal processing
• Drug design and pharmacokinetics
• Medical imaging analysis
• Biomaterials and tissue engineering
• FDA regulatory pathways

Feel free to ask about any of these topics, and I'll provide detailed technical information relevant to biomedical engineering practice.

**Note**: For full AI-powered responses with real-time information and complex reasoning, please configure your API key in the settings.""",
                
                """Welcome to the Biomedical Engineering Assistant demo mode! I can provide technical information on various biomedical topics even without an active API connection.

**System Capabilities:**
• Technical specifications and standards
• Regulatory guidance and compliance
• Algorithm implementations
• Material properties and testing
• Clinical trial design
• Signal processing techniques

Each response includes industry-standard metrics, relevant ISO/IEC standards, and practical implementation considerations for biomedical engineers.

Try asking about specific technical challenges or regulatory requirements in your biomedical engineering work!"""
            ]
        }
    
    def get_response(self, query: str) -> str:
        """Generate a mock response based on the query content."""
        query_lower = query.lower()
        
        # Keyword matching for topic selection
        if any(term in query_lower for term in ['crispr', 'gene', 'edit', 'cas9', 'genetic']):
            responses = self.response_templates['crispr']
        elif any(term in query_lower for term in ['ecg', 'ekg', 'cardiac', 'qrs', 'heart', 'arrhythmia']):
            responses = self.response_templates['ecg']
        elif any(term in query_lower for term in ['drug', 'pharmaceutical', 'compound', 'molecule', 'admet']):
            responses = self.response_templates['drug_design']
        elif any(term in query_lower for term in ['mri', 'ct', 'imaging', 'scan', 'dicom', 'segmentation']):
            responses = self.response_templates['imaging']
        elif any(term in query_lower for term in ['biomaterial', 'implant', 'scaffold', 'tissue', 'biocompat']):
            responses = self.response_templates['biomaterials']
        elif any(term in query_lower for term in ['fda', 'regulatory', '510k', 'clearance', 'approval', 'qsr']):
            responses = self.response_templates['regulatory']
        else:
            responses = self.response_templates['general']
        
        # Select a random response from the category
        return random.choice(responses)
    
    def get_streaming_response(self, query: str):
        """Generate a mock response with simulated streaming."""
        response = self.get_response(query)
        words = response.split()
        
        # Simulate streaming by yielding words in chunks
        chunk_size = random.randint(3, 7)  # Variable chunk sizes for realistic streaming
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            if i + chunk_size < len(words):
                chunk += ' '
            yield chunk
            time.sleep(random.uniform(0.05, 0.15))  # Simulate network delay

class MockToolExecutor:
    """Execute mock versions of biomedical tools."""
    
    @staticmethod
    def search_pubmed(query: str, max_results: int = 5) -> Dict[str, Any]:
        """Mock PubMed search with realistic results."""
        mock_papers = [
            {
                "title": f"Advanced {query} techniques in biomedical engineering: A systematic review",
                "authors": ["Zhang, L.", "Smith, J.R.", "Johnson, K.A."],
                "journal": "Nature Biomedical Engineering",
                "year": 2024,
                "pmid": f"38{random.randint(100000, 999999)}",
                "citations": random.randint(5, 150),
                "abstract": f"This systematic review examines recent advances in {query} applications..."
            },
            {
                "title": f"Machine learning approaches for {query} analysis in clinical settings",
                "authors": ["Patel, S.", "Williams, M.D.", "Chen, X."],
                "journal": "IEEE Transactions on Biomedical Engineering",
                "year": 2023,
                "pmid": f"37{random.randint(100000, 999999)}",
                "citations": random.randint(10, 200),
                "abstract": f"We present a novel ML framework for {query} that achieves..."
            },
            {
                "title": f"Clinical validation of {query}-based diagnostic systems",
                "authors": ["Brown, A.", "Davis, R.", "Miller, T."],
                "journal": "Medical Engineering & Physics",
                "year": 2024,
                "pmid": f"38{random.randint(100000, 999999)}",
                "citations": random.randint(3, 75),
                "abstract": f"Clinical validation study of {query} systems in 500 patients..."
            }
        ]
        
        return {
            "query": query,
            "num_results": min(len(mock_papers), max_results),
            "results": mock_papers[:max_results],
            "search_date": datetime.now().isoformat()
        }
    
    @staticmethod
    def analyze_sequence(sequence: str, sequence_type: str) -> Dict[str, Any]:
        """Mock sequence analysis with realistic metrics."""
        sequence = sequence.upper().strip()
        
        if sequence_type == "DNA":
            gc_count = sum(1 for base in sequence if base in "GC")
            gc_content = (gc_count / len(sequence)) * 100 if sequence else 0
            
            return {
                "sequence_type": "DNA",
                "length": len(sequence),
                "gc_content": f"{gc_content:.1f}%",
                "melting_temp": f"{4 * gc_count + 2 * (len(sequence) - gc_count):.1f}°C",
                "molecular_weight": f"{len(sequence) * 330:.1f} g/mol",
                "complement": sequence.translate(str.maketrans("ATGC", "TACG")),
                "gc_skew": f"{random.uniform(-0.1, 0.1):.3f}",
                "complexity": "Moderate" if gc_content > 40 and gc_content < 60 else "Low"
            }
        
        elif sequence_type == "protein":
            hydrophobic = sum(1 for aa in sequence if aa in "AILMFWYV")
            charged = sum(1 for aa in sequence if aa in "DEKR")
            
            return {
                "sequence_type": "protein",
                "length": len(sequence),
                "molecular_weight": f"{len(sequence) * 110:.1f} Da",
                "hydrophobic_ratio": f"{(hydrophobic/len(sequence)*100):.1f}%",
                "charged_residues": charged,
                "isoelectric_point": f"{random.uniform(4.5, 9.5):.1f}",
                "instability_index": f"{random.uniform(20, 50):.1f}",
                "gravy_score": f"{random.uniform(-2, 2):.2f}"
            }
        
        return {"error": "Unsupported sequence type"}
    
    @staticmethod
    def calculate_drug_properties(smiles: str, properties: List[str] = None) -> Dict[str, Any]:
        """Mock drug property calculations."""
        # Generate realistic-looking values
        mw = random.uniform(150, 500)
        logp = random.uniform(-1, 5)
        tpsa = random.uniform(20, 140)
        hbd = random.randint(0, 5)
        hba = random.randint(2, 10)
        
        result = {
            "smiles": smiles,
            "calculated_properties": {
                "molecular_weight": f"{mw:.2f} Da",
                "logP": f"{logp:.2f}",
                "tpsa": f"{tpsa:.2f} Ų",
                "hbd": hbd,
                "hba": hba,
                "rotatable_bonds": random.randint(0, 10),
                "aromatic_rings": random.randint(0, 4)
            },
            "drug_likeness": {
                "lipinski_violations": sum([
                    mw > 500,
                    logp > 5,
                    hbd > 5,
                    hba > 10
                ]),
                "qed_score": f"{random.uniform(0.3, 0.9):.2f}",
                "bioavailability": "High" if logp > 0 and logp < 3 else "Moderate"
            }
        }
        
        return result
