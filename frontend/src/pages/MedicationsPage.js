import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MedicationsPage = () => {
  const [medications, setMedications] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [checkingContraindications, setCheckingContraindications] = useState(false);
  const [contraindictionResult, setContraindictionResult] = useState(null);
  const [languages, setLanguages] = useState({});
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  
  const [newMed, setNewMed] = useState({
    name: '',
    dosage: '',
    frequency: '',
    timing: [],
    with_food: false
  });

  useEffect(() => {
    fetchLanguages();
    fetchMedications();
    fetchPrescriptions();
  }, []);

  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API}/languages`);
      setLanguages(response.data.languages);
    } catch (error) {
      console.error('Error fetching languages:', error);
    }
  };

  const fetchMedications = async () => {
    try {
      const response = await axios.get(`${API}/medications`);
      setMedications(response.data);
    } catch (error) {
      console.error('Error fetching medications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrescriptions = async () => {
    try {
      const response = await axios.get(`${API}/prescriptions`);
      setPrescriptions(response.data);
    } catch (error) {
      console.error('Error fetching prescriptions:', error);
    }
  };

  const handleAddMedication = async (e) => {
    e.preventDefault();
    
    if (!newMed.name || !newMed.dosage || !newMed.frequency) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/medications`, {
        ...newMed,
        preferred_language: selectedLanguage
      });
      toast.success('Medication added successfully! 🎉');
      setNewMed({
        name: '',
        dosage: '',
        frequency: '',
        timing: [],
        with_food: false
      });
      setShowAddForm(false);
      fetchMedications();
    } catch (error) {
      console.error('Error adding medication:', error);
      toast.error('Failed to add medication');
    } finally {
      setLoading(false);
    }
  };

  const checkContraindications = async (medicationName) => {
    const currentMedNames = [
      ...medications.map(m => m.name),
      ...prescriptions.flatMap(p => p.medications.map(m => m.name))
    ].filter(name => name !== medicationName);

    if (currentMedNames.length === 0) {
      toast.info('No other medications to check against');
      return;
    }

    setCheckingContraindications(true);
    try {
      const response = await axios.post(`${API}/contraindications/check`, {
        medication_name: medicationName,
        current_medications: currentMedNames,
        preferred_language: selectedLanguage
      });
      setContraindictionResult({ medication: medicationName, ...response.data });
    } catch (error) {
      console.error('Error checking contraindications:', error);
      toast.error('Failed to check contraindications');
    } finally {
      setCheckingContraindications(false);
    }
  };

  const allMedications = [
    ...medications,
    ...prescriptions.flatMap(p => p.medications)
  ];

  return (
    <div className="min-h-screen bg-paper py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="font-fraunces text-5xl md:text-7xl font-light leading-[0.95] text-stone-900 mb-4">
              My Medications
            </h1>
            <p className="text-lg md:text-xl leading-relaxed text-stone-600 font-jakarta">
              🌍 Manage medications from prescriptions in any language
            </p>
          </div>
          <div className="flex gap-3">
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="h-12 rounded-full border-stone-200 bg-white px-4 focus:ring-2 focus:ring-sage/20 focus:border-sage transition-all font-jakarta"
              data-testid="language-selector-medications"
            >
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="rounded-full bg-sage text-white px-6 py-3 font-semibold font-jakarta shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0 whitespace-nowrap"
              data-testid="add-medication-button"
            >
              {showAddForm ? 'Cancel' : '+ Add Medication'}
            </button>
          </div>
        </div>

        {showAddForm && (
          <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 mb-12" data-testid="add-medication-form">
            <h2 className="font-fraunces text-3xl font-semibold text-stone-900 mb-6">
              Add Medication Manually
            </h2>
            <form onSubmit={handleAddMedication} className="space-y-4">
              <div>
                <label className="block text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                  Medication Name *
                </label>
                <input
                  type="text"
                  value={newMed.name}
                  onChange={(e) => setNewMed({...newMed, name: e.target.value})}
                  className="w-full h-14 rounded-2xl border-stone-200 bg-stone-50 px-4 focus:ring-2 focus:ring-sage/20 focus:border-sage transition-all text-lg font-jakarta"
                  placeholder="e.g., Metformin"
                  data-testid="medication-name-input"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                    Dosage *
                  </label>
                  <input
                    type="text"
                    value={newMed.dosage}
                    onChange={(e) => setNewMed({...newMed, dosage: e.target.value})}
                    className="w-full h-14 rounded-2xl border-stone-200 bg-stone-50 px-4 focus:ring-2 focus:ring-sage/20 focus:border-sage transition-all text-lg font-jakarta"
                    placeholder="e.g., 500mg"
                    data-testid="medication-dosage-input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                    Frequency *
                  </label>
                  <input
                    type="text"
                    value={newMed.frequency}
                    onChange={(e) => setNewMed({...newMed, frequency: e.target.value})}
                    className="w-full h-14 rounded-2xl border-stone-200 bg-stone-50 px-4 focus:ring-2 focus:ring-sage/20 focus:border-sage transition-all text-lg font-jakarta"
                    placeholder="e.g., Twice daily"
                    data-testid="medication-frequency-input"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                  Timing
                </label>
                <div className="flex flex-wrap gap-3">
                  {['morning', 'afternoon', 'evening', 'night', 'with meals'].map((time) => (
                    <label key={time} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newMed.timing.includes(time)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewMed({...newMed, timing: [...newMed.timing, time]});
                          } else {
                            setNewMed({...newMed, timing: newMed.timing.filter(t => t !== time)});
                          }
                        }}
                        className="w-5 h-5 rounded border-stone-300 text-sage focus:ring-sage"
                      />
                      <span className="text-stone-700 font-jakarta capitalize">{time}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="with-food"
                  checked={newMed.with_food}
                  onChange={(e) => setNewMed({...newMed, with_food: e.target.checked})}
                  className="w-5 h-5 rounded border-stone-300 text-sage focus:ring-sage"
                  data-testid="with-food-checkbox"
                />
                <label htmlFor="with-food" className="text-stone-700 font-jakarta cursor-pointer">
                  Take with food
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-full bg-sage text-white px-8 py-4 font-semibold font-jakarta shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50"
                data-testid="submit-medication-button"
              >
                {loading ? 'Adding...' : 'Add Medication'}
              </button>
            </form>
          </div>
        )}

        {loading && allMedications.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-stone-600 font-jakarta">Loading medications...</p>
          </div>
        ) : allMedications.length === 0 ? (
          <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-12 text-center">
            <div className="w-20 h-20 bg-sage/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-4xl">💊</span>
            </div>
            <h3 className="font-fraunces text-2xl font-semibold text-stone-900 mb-2">
              No medications yet
            </h3>
            <p className="text-stone-600 font-jakarta">
              Upload a prescription or add medications manually to get started
            </p>
          </div>
        ) : (
          <div className="space-y-4" data-testid="medications-list">
            {allMedications.map((medication, index) => (
              <div
                key={medication.id || index}
                className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-shadow duration-300"
                data-testid={`medication-item-${index}`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-fraunces text-2xl md:text-3xl font-semibold text-stone-900">
                      {medication.name}
                    </h3>
                    <p className="text-stone-600 font-jakarta mt-1">
                      {medication.dosage} • {medication.frequency}
                    </p>
                    {medication.translated_to && (
                      <span className="inline-block mt-2 bg-sage/10 text-sage px-3 py-1 rounded-full text-xs font-jakarta font-medium">
                        🌐 Translated to {languages[medication.translated_to] || 'English'}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    {medication.with_food && (
                      <span className="bg-clay/10 text-clay px-4 py-2 rounded-full text-sm font-jakarta font-medium">
                        🍽️ Take with food
                      </span>
                    )}
                    <button
                      onClick={() => checkContraindications(medication.name)}
                      disabled={checkingContraindications}
                      className="bg-stone-100 hover:bg-stone-200 text-stone-700 px-4 py-2 rounded-full text-sm font-jakarta font-medium transition-colors duration-300"
                      data-testid={`check-contraindications-${index}`}
                    >
                      Check Safety
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                      💊 What it does
                    </h4>
                    <p className="text-stone-700 font-jakarta leading-relaxed">
                      {medication.plain_language_explanation}
                    </p>
                  </div>

                  <div className="bg-sage/5 p-4 rounded-2xl">
                    <h4 className="text-sm font-bold uppercase tracking-widest text-sage font-jakarta mb-2">
                      ⏰ Why timing matters
                    </h4>
                    <p className="text-stone-700 font-jakarta leading-relaxed">
                      {medication.why_timing_matters}
                    </p>
                  </div>

                  {medication.warnings && medication.warnings.length > 0 && medication.warnings[0] && (
                    <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-2xl">
                      <h4 className="text-sm font-bold uppercase tracking-widest text-yellow-700 font-jakarta mb-2">
                        ⚠️ Important Safety
                      </h4>
                      {medication.warnings.map((warning, idx) => (
                        warning && <p key={idx} className="text-stone-700 font-jakarta">{warning}</p>
                      ))}
                    </div>
                  )}

                  {medication.timing && medication.timing.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      <span className="text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mr-2">
                        Timing:
                      </span>
                      {medication.timing.map((time, idx) => (
                        <span
                          key={idx}
                          className="bg-stone-100 text-stone-700 px-3 py-1 rounded-full text-sm font-jakarta"
                        >
                          {time}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {contraindictionResult && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" data-testid="contraindication-modal">
            <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.2)] p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex items-start justify-between mb-6">
                <h3 className="font-fraunces text-3xl font-semibold text-stone-900">
                  Safety Check: {contraindictionResult.medication}
                </h3>
                <button
                  onClick={() => setContraindictionResult(null)}
                  className="text-stone-500 hover:text-stone-700"
                  data-testid="close-modal-button"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                {contraindictionResult.has_contraindications ? (
                  <div className="bg-red-50 border border-red-200 p-4 rounded-2xl">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-2xl">⚠️</span>
                      <h4 className="text-sm font-bold uppercase tracking-widest text-red-700 font-jakarta">
                        Potential Contraindications Found
                      </h4>
                    </div>
                    <ul className="space-y-2 mt-3">
                      {contraindictionResult.warnings.map((warning, idx) => (
                        <li key={idx} className="text-stone-700 font-jakarta flex items-start space-x-2">
                          <span className="text-red-500 mt-1">•</span>
                          <span>{warning}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="bg-green-50 border border-green-200 p-4 rounded-2xl">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">✅</span>
                      <h4 className="text-sm font-bold uppercase tracking-widest text-green-700 font-jakarta">
                        No Contraindications Found
                      </h4>
                    </div>
                  </div>
                )}

                <div className="bg-stone-50 p-4 rounded-2xl">
                  <h4 className="text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                    Recommendations
                  </h4>
                  <p className="text-stone-700 font-jakarta leading-relaxed">
                    {contraindictionResult.recommendations}
                  </p>
                </div>

                <p className="text-sm text-stone-500 font-jakarta italic">
                  Note: This is a basic check. Always consult your doctor or pharmacist for professional medical advice.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MedicationsPage;