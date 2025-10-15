import React from 'react';

export default function ActivityCard({ activity }) {
  return (
    <div className="activity-card">
      <h4>{activity.title}</h4>
      <p>{activity.description}</p>
      <p>
        <strong>Date:</strong> {new Date(activity.date).toLocaleDateString()}
      </p>
      <p>
        <strong>Time:</strong> {new Date(activity.date).toLocaleTimeString()}
      </p>
      <p>
        <strong>Location:</strong> {activity.location}
      </p>
      {/* Participants section */}
      <div className="activity-card-participants">
        <div className="activity-card-participants-title">Participants</div>
        <ul className="activity-card-participants-list">
          {activity.participants && activity.participants.length > 0 ? (
            activity.participants.map((participant, idx) => (
              <li key={idx}>{participant}</li>
            ))
          ) : (
            <li>No participants yet</li>
          )}
        </ul>
      </div>
    </div>
  );
}