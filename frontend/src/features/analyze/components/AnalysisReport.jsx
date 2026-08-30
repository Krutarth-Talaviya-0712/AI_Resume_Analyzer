/**
 * AnalysisReport
 * --------------
 * Renders the detailed breakdown of an analysis result.
 * Shows: section detection, contact signals, formatting stats,
 * quantification, detected skills, and actionable feedback.
 *
 * Props:
 *   report {object} — full analysis response from /api/analyze/upload
 */

const SectionBadge = ({ label, detected }) => (
  <span
    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
      detected
        ? 'bg-green-50 text-green-700 border-green-200'
        : 'bg-gray-100 text-gray-400 border-gray-200'
    }`}
  >
    <span className={`w-1.5 h-1.5 rounded-full ${detected ? 'bg-green-500' : 'bg-gray-300'}`} />
    {label}
  </span>
);

const StatCard = ({ label, value, sub }) => (
  <div className="bg-gray-50 rounded-xl p-4 text-center border border-gray-100">
    <p className="text-2xl font-extrabold text-gray-900">{value}</p>
    <p className="text-xs font-semibold text-gray-500 mt-0.5">{label}</p>
    {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
  </div>
);

const FeedbackItem = ({ text, type }) => (
  <li className={`flex items-start gap-3 text-sm ${type === 'strength' ? 'text-gray-700' : 'text-gray-700'}`}>
    <span
      className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
        type === 'strength'
          ? 'bg-green-100 text-green-600'
          : 'bg-amber-100 text-amber-600'
      }`}
    >
      {type === 'strength' ? '+' : '!'}
    </span>
    <span className="leading-relaxed">{text}</span>
  </li>
);

const SECTION_LIST = [
  { key: 'experience', label: 'Experience' },
  { key: 'education', label: 'Education' },
  { key: 'skills', label: 'Skills' },
  { key: 'summary', label: 'Summary' },
  { key: 'projects', label: 'Projects' },
  { key: 'certifications', label: 'Certifications' },
  { key: 'languages', label: 'Languages' },
  { key: 'interests', label: 'Interests' },
  { key: 'contact', label: 'Contact' },
];

const AnalysisReport = ({ report }) => {
  const { stats, detected_sections, technical_skills, soft_skills, strengths, improvements } = report;
  const detectedSet = new Set(detected_sections || []);

  // ATS sub-score bars
  const atsBreakdown = report.ats_breakdown || {};
  const atsLabels = {
    contact_info: 'Contact Info',
    sections: 'Section Structure',
    keyword_density: 'Keyword Density',
    formatting: 'Formatting',
    quantification: 'Quantification',
  };
  const atsMaxValues = {
    contact_info: 10,
    sections: 25,
    keyword_density: 30,
    formatting: 15,
    quantification: 20,
  };

  return (
    <div className="space-y-8">

      {/* Document Stats */}
      <section>
        <h3 className="text-base font-bold text-gray-900 mb-4">Document Statistics</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard label="Words" value={stats?.word_count ?? '—'} sub="300-700 is ideal" />
          <StatCard label="Sentences" value={stats?.sentence_count ?? '—'} />
          <StatCard label="Bullet Points" value={stats?.bullet_count ?? '—'} sub="Aim for 8+" />
          <StatCard label="Quantified Wins" value={stats?.quantification_count ?? '—'} sub="Aim for 5+" />
        </div>
      </section>

      {/* Contact Signals */}
      <section>
        <h3 className="text-base font-bold text-gray-900 mb-3">Contact & Links</h3>
        <div className="flex flex-wrap gap-2">
          <SectionBadge label="Email Address" detected={stats?.has_email} />
          <SectionBadge label="Phone Number" detected={stats?.has_phone} />
          <SectionBadge label="LinkedIn / URL" detected={stats?.has_url} />
        </div>
      </section>

      {/* Section Detection */}
      <section>
        <h3 className="text-base font-bold text-gray-900 mb-3">Detected Sections</h3>
        <div className="flex flex-wrap gap-2">
          {SECTION_LIST.map(({ key, label }) => (
            <SectionBadge key={key} label={label} detected={detectedSet.has(key)} />
          ))}
        </div>
      </section>

      {/* ATS Score Breakdown */}
      <section>
        <h3 className="text-base font-bold text-gray-900 mb-4">ATS Score Breakdown</h3>
        <div className="space-y-3">
          {Object.entries(atsLabels).map(([key, label]) => {
            const raw = atsBreakdown[key] ?? 0;
            const max = atsMaxValues[key];
            const pct = Math.min((raw / max) * 100, 100);
            const barColor = pct >= 75 ? '#22c55e' : pct >= 45 ? '#3b82f6' : '#f59e0b';
            return (
              <div key={key}>
                <div className="flex justify-between text-xs font-medium text-gray-600 mb-1">
                  <span>{label}</span>
                  <span>{raw.toFixed(1)} / {max}</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${pct}%`, backgroundColor: barColor }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Technical Skills */}
      <section>
        <h3 className="text-base font-bold text-gray-900 mb-3">
          Technical Skills Detected
          <span className="ml-2 text-sm font-normal text-gray-400">({(technical_skills || []).length} found)</span>
        </h3>
        {(technical_skills || []).length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {technical_skills.map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 bg-blue-50 border border-blue-100 text-blue-700 text-xs font-medium rounded-lg capitalize"
              >
                {skill}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400 italic">No technical skills detected. Add a Skills section.</p>
        )}
      </section>

      {/* Soft Skills */}
      {(soft_skills || []).length > 0 && (
        <section>
          <h3 className="text-base font-bold text-gray-900 mb-3">
            Soft Skills Detected
            <span className="ml-2 text-sm font-normal text-gray-400">({soft_skills.length} found)</span>
          </h3>
          <div className="flex flex-wrap gap-2">
            {soft_skills.map((skill) => (
              <span
                key={skill}
                className="px-3 py-1 bg-purple-50 border border-purple-100 text-purple-700 text-xs font-medium rounded-lg capitalize"
              >
                {skill}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Strengths */}
      {(strengths || []).length > 0 && (
        <section>
          <h3 className="text-base font-bold text-gray-900 mb-3">Strengths</h3>
          <ul className="space-y-2.5">
            {strengths.map((s, i) => (
              <FeedbackItem key={i} text={s} type="strength" />
            ))}
          </ul>
        </section>
      )}

      {/* Areas for Improvement */}
      {(improvements || []).length > 0 && (
        <section>
          <h3 className="text-base font-bold text-gray-900 mb-3">Areas for Improvement</h3>
          <ul className="space-y-2.5">
            {improvements.map((s, i) => (
              <FeedbackItem key={i} text={s} type="improvement" />
            ))}
          </ul>
        </section>
      )}

    </div>
  );
};

export default AnalysisReport;
