import React from 'react';
import './PanelBox.css';

interface PanelBoxProps {
  title: string;
  children: React.ReactNode;
  doubleLine?: boolean;
  style?: React.CSSProperties;
}

export function PanelBox({ title, children, doubleLine, style }: PanelBoxProps) {
  return (
    <div className={`panel-box ${doubleLine ? 'panel-box--double' : ''}`} style={style}>
      <div className="panel-box__header">
        {doubleLine ? '╔' : '┌'}{'─ [ '}{title}{' ] '}
        {'─'.repeat(Math.max(0, 50 - title.length))}
        {doubleLine ? '╗' : '┐'}
      </div>
      <div className="panel-box__content">
        {children}
      </div>
      <div className="panel-box__footer">
        {doubleLine ? '╚' : '└'}{'─'.repeat(56)}{doubleLine ? '╝' : '┘'}
      </div>
    </div>
  );
}
