import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UploadPage = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a prescription image first');
      return;
    }

    setLoading(true);
    try {
      const base64Image = await convertToBase64(selectedFile);
      
      const response = await axios.post(`${API}/prescriptions/upload`, {
        image_base64: base64Image,
        patient_id: 'default-patient'
      });

      setResult(response.data);
      toast.success('Prescription analyzed successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to analyze prescription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-paper py-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12">
          <h1 className="font-fraunces text-5xl md:text-7xl font-light leading-[0.95] text-stone-900 mb-4">
            Upload Your Prescription
          </h1>
          <p className="text-lg md:text-xl leading-relaxed text-stone-600 font-jakarta">
            Take a clear photo of your prescription. Our AI will extract and explain all medications.
          </p>
        </div>

        <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8">
          <div className="space-y-6">
            <div>
              <label
                htmlFor="file-upload"
                className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-stone-300 rounded-2xl cursor-pointer bg-stone-50 hover:bg-stone-100 transition-colors duration-300"
                data-testid="file-upload-area"
              >
                {previewUrl ? (
                  <img src={previewUrl} alt="Preview" className="h-full object-contain rounded-2xl" />
                ) : (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <svg className="w-16 h-16 mb-4 text-sage" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="mb-2 text-sm text-stone-700 font-jakarta">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-stone-500 font-jakarta">PNG, JPG, JPEG, or WEBP</p>
                  </div>
                )}
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  onChange={handleFileSelect}
                  data-testid="file-input"
                />
              </label>
            </div>

            {selectedFile && (
              <div className="flex items-center justify-between bg-sage/5 p-4 rounded-2xl">
                <span className="text-sm text-stone-700 font-jakarta truncate">{selectedFile.name}</span>
                <button
                  onClick={() => {
                    setSelectedFile(null);
                    setPreviewUrl(null);
                    setResult(null);
                  }}
                  className="text-stone-500 hover:text-stone-700"
                  data-testid="clear-file-button"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}

            <button
              onClick={handleUpload}
              disabled={!selectedFile || loading}
              className="w-full rounded-full bg-sage text-white px-8 py-4 font-semibold font-jakarta shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="analyze-button"
            >
              {loading ? 'Analyzing...' : 'Analyze Prescription'}
            </button>
          </div>
        </div>

        {result && (
          <div className="mt-12 space-y-6" data-testid="analysis-results">
            <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8">
              <h2 className="font-fraunces text-3xl font-semibold text-stone-900 mb-4">
                Extracted Text
              </h2>
              <p className="text-stone-700 font-jakarta whitespace-pre-wrap">{result.extracted_text}</p>
            </div>

            <div>
              <h2 className="font-fraunces text-3xl font-semibold text-stone-900 mb-6">
                Your Medications
              </h2>
              <div className="space-y-4">
                {result.medications.map((medication, index) => (
                  <div
                    key={medication.id || index}
                    className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8"
                    data-testid={`medication-card-${index}`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-fraunces text-2xl font-semibold text-stone-900">
                          {medication.name}
                        </h3>
                        <p className="text-stone-600 font-jakarta mt-1">
                          {medication.dosage} • {medication.frequency}
                        </p>
                      </div>
                      {medication.with_food && (
                        <span className="bg-clay/10 text-clay px-4 py-2 rounded-full text-sm font-jakarta font-medium">
                          Take with food
                        </span>
                      )}
                    </div>

                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-bold uppercase tracking-widest text-stone-500 font-jakarta mb-2">
                          What it does
                        </h4>
                        <p className="text-stone-700 font-jakarta leading-relaxed">
                          {medication.plain_language_explanation}
                        </p>
                      </div>

                      <div className="bg-sage/5 p-4 rounded-2xl">
                        <h4 className="text-sm font-bold uppercase tracking-widest text-sage font-jakarta mb-2">
                          Why timing matters
                        </h4>
                        <p className="text-stone-700 font-jakarta leading-relaxed">
                          {medication.why_timing_matters}
                        </p>
                      </div>

                      {medication.timing && medication.timing.length > 0 && (
                        <div className="flex flex-wrap gap-2">
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
            </div>

            <div className="flex justify-center pt-6">
              <button
                onClick={() => navigate('/medications')}
                className="rounded-full bg-clay text-white px-8 py-4 font-semibold font-jakarta shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0"
                data-testid="view-all-medications-button"
              >
                View All My Medications
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPage;