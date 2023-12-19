import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Success = () => {
    const [countdown, setCountdown] = useState(5);
    const tickGifUrl = 'https://i.ibb.co/TtwkTvy/success.gif'; // Replace with your actual GIF URL
    const navigate = useNavigate()
  
    useEffect(() => {
      const interval = setInterval(() => {
        setCountdown((prevCountdown) => prevCountdown - 1);
      }, 1000);
  
      const timeout = setTimeout(() => {
        clearInterval(interval);
        navigate("/") // This function should handle the redirection logic
      }, 5000);
  
      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }, []);
    return (
        <div className="text-center">
            <img src={tickGifUrl} alt="Success" />
            <p>Payment complete, redirecting in {countdown} secs</p>
        </div>
    );
};

export default Success;
