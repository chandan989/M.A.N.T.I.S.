import { useState, useCallback } from 'react';
import { useAgent } from '../../context/AgentContext';
import './ConfirmModal.css';

interface ConfirmModalProps {
  title: string;
  message: string;
  targetLabel?: string;
  actionLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'danger' | 'info';
}

const PROGRESS_STEPS = ['[█░░░░]', '[███░░]', '[█████]', '[  OK  ]'];

export function ConfirmModal({ title, message, targetLabel, actionLabel = 'EXECUTE', onConfirm, onCancel, variant = 'info' }: ConfirmModalProps) {
  const { state, dispatch } = useAgent();
  const [step, setStep] = useState(-1);
  const executing = step >= 0;

  const handleExecute = useCallback(() => {
    dispatch({ type: 'SET_ACTION_IN_FLIGHT', payload: true });
    setStep(0);
    let s = 0;
    const timer = setInterval(() => {
      s++;
      if (s >= PROGRESS_STEPS.length) {
        clearInterval(timer);
        dispatch({ type: 'SET_ACTION_IN_FLIGHT', payload: false });
        onConfirm();
      } else {
        setStep(s);
      }
    }, 375);
  }, [dispatch, onConfirm]);

  return (
    <div className="confirm-overlay" onClick={!executing ? onCancel : undefined}>
      <div style={{ position: 'relative' }}>
        <div className="confirm-shadow" />
        <div
          className={`confirm-modal ${variant === 'danger' ? 'confirm-modal--danger' : ''}`}
          onClick={e => e.stopPropagation()}
        >
          <div className="confirm-modal__title">{'┌─ [ '}{title}{' ] ─┐'}</div>
          <div className="confirm-modal__message">{message}</div>
          {targetLabel && <div className="confirm-modal__target">TARGET: {targetLabel}</div>}
          <div className="confirm-modal__actions">
            <button className="btn" onClick={onCancel} disabled={executing}>[ CANCEL ]</button>
            <button
              className={`btn ${variant === 'danger' ? 'btn--danger' : ''} ${executing ? 'btn--loading' : ''}`}
              onClick={handleExecute}
              disabled={executing || state.actionInFlight}
            >
              {executing ? PROGRESS_STEPS[step] : `[ ${actionLabel} ]`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
