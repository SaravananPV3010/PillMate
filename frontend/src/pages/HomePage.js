import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-paper">
      <section className="py-24 md:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
            <div className="md:col-span-7 space-y-8">
              <h1 className="font-fraunces text-5xl md:text-7xl font-light leading-[0.95] text-stone-900">
                Never Miss a Dose,
                <span className="block text-sage mt-2">Understand the Why</span>
              </h1>
              
              <p className="text-lg md:text-xl leading-relaxed text-stone-600 font-jakarta max-w-2xl">
                Transform complex prescriptions into simple, personalized adherence plans. 
                Our AI explains not just <em>what</em> to take, but <em>why timing matters</em> — because understanding leads to better health outcomes.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <button
                  data-testid="upload-prescription-button"
                  onClick={() => navigate('/upload')}
                  className="rounded-full bg-sage text-white px-8 py-4 font-semibold font-jakarta shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0"
                >
                  Upload Prescription
                </button>
                <button
                  data-testid="view-medications-button"
                  onClick={() => navigate('/medications')}
                  className="rounded-full border-2 border-sage text-sage px-8 py-4 font-semibold font-jakarta hover:bg-sage/10 transition-all duration-300"
                >
                  View My Medications
                </button>
              </div>
            </div>

            <div className="md:col-span-5">
              <div className="rounded-3xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
                <img
                  src="https://images.unsplash.com/photo-1590905775253-a4f0f3c426ff?crop=entropy&cs=srgb&fm=jpg&q=85"
                  alt="Confident elderly woman"
                  className="w-full h-auto"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-white/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="font-fraunces text-4xl md:text-5xl font-normal leading-tight text-stone-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-stone-600 font-jakarta">Three simple steps to better medication adherence</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-shadow duration-300">
              <div className="w-16 h-16 bg-sage/10 rounded-full flex items-center justify-center mb-6">
                <span className="text-3xl">📸</span>
              </div>
              <h3 className="font-fraunces text-2xl md:text-3xl font-semibold text-stone-900 mb-3">
                1. Upload
              </h3>
              <p className="text-base leading-relaxed text-stone-600 font-jakarta">
                Take a photo of your prescription or enter medication details manually. Our AI handles multiple languages and handwriting.
              </p>
            </div>

            <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-shadow duration-300">
              <div className="w-16 h-16 bg-sage/10 rounded-full flex items-center justify-center mb-6">
                <span className="text-3xl">🧠</span>
              </div>
              <h3 className="font-fraunces text-2xl md:text-3xl font-semibold text-stone-900 mb-3">
                2. Understand
              </h3>
              <p className="text-base leading-relaxed text-stone-600 font-jakarta">
                Get plain-language explanations of what each medication does and why timing matters. No medical jargon.
              </p>
            </div>

            <div className="bg-white rounded-3xl border border-stone-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] transition-shadow duration-300">
              <div className="w-16 h-16 bg-sage/10 rounded-full flex items-center justify-center mb-6">
                <span className="text-3xl">✅</span>
              </div>
              <h3 className="font-fraunces text-2xl md:text-3xl font-semibold text-stone-900 mb-3">
                3. Stay On Track
              </h3>
              <p className="text-base leading-relaxed text-stone-600 font-jakarta">
                Receive personalized reminders with behavioral nudges that help you remember and understand the importance of each dose.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
            <div className="md:col-span-5">
              <div className="rounded-3xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
                <img
                  src="https://images.unsplash.com/photo-1563213126-a4273aed2016?crop=entropy&cs=srgb&fm=jpg&q=85"
                  alt="Organizing medication"
                  className="w-full h-auto"
                />
              </div>
            </div>

            <div className="md:col-span-7 space-y-6">
              <h2 className="font-fraunces text-4xl md:text-5xl font-normal leading-tight text-stone-900">
                Built on Behavioral Science
              </h2>
              <p className="text-lg md:text-xl leading-relaxed text-stone-600 font-jakarta">
                We use <strong>Nudge Theory</strong> to increase medication adherence. Instead of simple reminders, 
                we explain <em>why</em> each dose matters — connecting your actions to better health outcomes.
              </p>
              <ul className="space-y-4 text-stone-700 font-jakarta">
                <li className="flex items-start space-x-3">
                  <span className="text-sage text-xl mt-1">✓</span>
                  <span>Check for basic contraindications with your current medications</span>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-sage text-xl mt-1">✓</span>
                  <span>Plain-language explanations anyone can understand</span>
                </li>
                <li className="flex items-start space-x-3">
                  <span className="text-sage text-xl mt-1">✓</span>
                  <span>Personalized reminders that actually motivate</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-sage/5 py-12 mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-stone-600 font-jakarta">© 2026 PillGuide. Helping you stay on track, one dose at a time.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;