/**
 * JobSuggestions
 * --------------
 * Renders a grid of job role cards ranked by match score.
 * Each card shows matched skills, missing skills, and a visual fit bar.
 *
 * Props:
 *   suggestions {Array} — array of job suggestion objects from the API
 *   {
 *     title: string,
 *     match_score: number (0-100),
 *     matched_skills: string[],
 *     missing_skills: string[],
 *   }
 */

const MatchBar = ({ score }) => {
  const color = score >= 70 ? '#22c55e' : score >= 45 ? '#3b82f6' : '#f59e0b';
  return (
    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: `${score}%`, backgroundColor: color }}
      />
    </div>
  );
};

const ScoreBadge = ({ score }) => {
  let colorClass = 'bg-amber-100 text-amber-700';
  if (score >= 70) colorClass = 'bg-green-100 text-green-700';
  else if (score >= 45) colorClass = 'bg-blue-100 text-blue-700';

  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${colorClass}`}>
      {score}% match
    </span>
  );
};

const JobSuggestions = ({ suggestions }) => {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="text-center py-10 text-gray-400 text-sm">
        No job suggestions available. Ensure your resume includes a Skills section.
      </div>
    );
  }

  return (
    <div>
      <p className="text-sm text-gray-500 mb-5">
        Roles are ranked by how closely your detected skills match the typical requirements
        for each position, calculated using TF-IDF cosine similarity.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {suggestions.map((job, index) => (
          <div
            key={job.title}
            className="relative bg-white rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-all p-5 flex flex-col gap-3"
          >
            {/* Rank badge */}
            <div className="absolute top-3 right-3 w-7 h-7 rounded-full bg-gray-100 text-gray-400 text-xs font-bold flex items-center justify-center">
              #{index + 1}
            </div>

            {/* Role title + score badge */}
            <div className="pr-8">
              <h4 className="font-bold text-gray-900 text-base leading-tight">{job.title}</h4>
              <div className="mt-1.5">
                <ScoreBadge score={job.match_score} />
              </div>
            </div>

            {/* Match bar */}
            <MatchBar score={job.match_score} />

            {/* Matched skills */}
            {(job.matched_skills || []).length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1.5">Skills you have</p>
                <div className="flex flex-wrap gap-1.5">
                  {job.matched_skills.slice(0, 6).map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-0.5 bg-green-50 border border-green-100 text-green-700 text-xs font-medium rounded-md capitalize"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing skills */}
            {(job.missing_skills || []).length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 mb-1.5">Skills to consider adding</p>
                <div className="flex flex-wrap gap-1.5">
                  {job.missing_skills.slice(0, 5).map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-0.5 bg-gray-50 border border-gray-200 text-gray-500 text-xs font-medium rounded-md capitalize"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JobSuggestions;
