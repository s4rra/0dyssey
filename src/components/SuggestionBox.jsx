import React, { Fragment } from "react";
import { MessageSquare, X } from "lucide-react";

const SuggestionBox = ({
  unitId,
  unitSummary,
  unitLocked,
  feedbackHandled,
  showPrompt,
  handleLevelOk,
  onDismissPrompt
}) => {
  return (
    <div className="card suggestion-box">
      <div className="card-header">
        <h3>Quick Note</h3>
        <MessageSquare className="card-icon" />
      </div>

      {unitLocked || !unitSummary ? (
        <p>Keep going! Finish Unit {unitId} to get feedback.</p>
      ) : feedbackHandled ? (
        <p>Keep going! Finish Unit {unitId} for your next AI review.</p>
      ) : (
        <Fragment>
          <p className="note-text">{unitSummary.summary}</p>
          {showPrompt && (
            <>
              <p className="suggestion-text">{unitSummary.prompt}</p>
              <div className="btn-row">
                <button className="btn confirm" onClick={handleLevelOk}>OK</button>
                <button className="btn cancel" onClick={onDismissPrompt}>
                  <X size={14} />
                </button>
              </div>
            </>
          )}
        </Fragment>
      )}
    </div>
  );
};

export default SuggestionBox;
