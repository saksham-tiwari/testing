import * as React from "react";

export function YearDropdown({ date, locale, onChange }) {
  const [year, setYear] = React.useState(date.getFullYear());

  const handleChange = (event) => {
    const newYear = Number(event.target.value);
    setYear(newYear);

    const newDate = new Date(date);
    newDate.setFullYear(newYear);
    onChange(newDate);
  };

  const years = Array.from({ length: 20 }, (_, i) => new Date().getFullYear() - i);

  return (
    <select value={year} onChange={handleChange}>
      {years.map((year) => (
        <option key={year} value={year}>
          {year}
        </option>
      ))}
    </select>
  );
}
