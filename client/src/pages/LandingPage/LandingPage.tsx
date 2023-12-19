import { Button } from "@/components/ui/button";
import CalendarHeader from "@/components/CalendarHeader/CalendarHeader";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { format } from "date-fns";
import { BaseURL } from "@/Constant";

// Suppose this is your timeslot object
const timeSlots = {
  morning: "9:00 AM - 11:00 AM",
  noon: "12:00 PM - 2:00 PM",
  afternoon: "3:00 PM - 5:00 PM",
  evening: "6:00 PM - 8:00 PM",
};

const timeSlotsUTC = {
  "morning": "T06:00:00Z",
  "noon": "T07:00:00Z",
  "afternoon": "T08:00:00Z",
  "evening": "T17:00:00Z",
};

const LandingPage = () => {
  const [selectedSlot, setSelectedSlot] = useState("");
  const [currentDate, setCurrentDate] = useState(new Date());
  const navigate = useNavigate();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const handleSlotClick = (key:any) => {
    setSelectedSlot(key);
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const isKeyOfTimeSlotsUTC = (key: any): key is keyof typeof timeSlotsUTC => {
    return key in timeSlotsUTC;
  }

  const submit = () => {
    console.log(selectedSlot);
    const formattedDate = {
      year: format(currentDate, "yyyy"),
      month: format(currentDate, "MM"),
    };
    let dateStringStart: string
    if (isKeyOfTimeSlotsUTC(selectedSlot)) {
      dateStringStart = `${formattedDate.year}-${formattedDate.month}-01${timeSlotsUTC[selectedSlot]}`;
    }

    axios
      .post(`${BaseURL}get-slots/`, formattedDate)
      .then((res) => {
        console.log(res.data);
        if (res.data.timings) {
          const timing = res.data.timings.find(
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (element : any) => element.start_time === dateStringStart
          );
          if (timing) {
            navigate("/register", { state: { id: timing.external_id } });
          } else {
            console.log("No matching timing found");
          }
        } else if (res.data.message) {
          alert(res.data.message);
        }
      })
      .catch((err) => {
        console.error(err);
      });
  };

  return (
    <>
      <CalendarHeader
        currentDate={currentDate}
        setCurrentDate={setCurrentDate}
      />

      <div className="grid grid-cols-2 gap-4 mb-6">
        {Object.entries(timeSlots).map(([key, value]) => (
          <div
            key={key}
            className={`p-4 border rounded-lg shadow-sm cursor-pointer ${
              selectedSlot === key
                ? "border-gray-700 font-semibold"
                : "border-gray-300"
            }`}
            onClick={() => handleSlotClick(key)}
          >
            <div className={`font-medium capitalize`}>{key}</div>
            <div>{value}</div>
          </div>
        ))}
      </div>

      <Button className="w-full" disabled={!selectedSlot} onClick={submit}>
        Submit
      </Button>
    </>
  );
};

export default LandingPage;
