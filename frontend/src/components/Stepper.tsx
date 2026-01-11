import { Check } from 'lucide-react';
import { clsx } from 'clsx';

interface Step {
  id: number;
  name: string;
  description: string;
}

interface StepperProps {
  steps: Step[];
  currentStep: number;
}

export default function Stepper({ steps, currentStep }: StepperProps) {
  return (
    <nav aria-label="Progress">
      <ol className="flex items-center justify-between">
        {steps.map((step, index) => (
          <li key={step.id} className="relative flex-1">
            {index !== steps.length - 1 && (
              <div
                className={clsx(
                  'absolute top-5 left-1/2 w-full h-0.5',
                  currentStep > index ? 'bg-primary-600' : 'bg-gray-200'
                )}
                aria-hidden="true"
              />
            )}
            
            <div className="relative flex flex-col items-center group">
              <span
                className={clsx(
                  'w-10 h-10 flex items-center justify-center rounded-full border-2 transition-all duration-200',
                  currentStep === index
                    ? 'bg-primary-600 border-primary-600 text-white'
                    : currentStep > index
                    ? 'bg-primary-600 border-primary-600 text-white'
                    : 'bg-white border-gray-300 text-gray-500'
                )}
              >
                {currentStep > index ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </span>
              
              <div className="mt-3 text-center hidden sm:block">
                <span
                  className={clsx(
                    'text-sm font-medium',
                    currentStep >= index ? 'text-primary-600' : 'text-gray-500'
                  )}
                >
                  {step.name}
                </span>
                <p className="text-xs text-gray-400 mt-0.5">{step.description}</p>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </nav>
  );
}
