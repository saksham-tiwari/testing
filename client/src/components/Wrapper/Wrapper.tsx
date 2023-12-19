import React from 'react';

type Props = {
    children: React.ReactNode
}

const Wrapper:React.FC<Props> = ({children}) => {

    return (
        <div className="min-h-screen bg-gray-50 p-8 flex justify-center items-center">
            <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
                {children}
            </div>
        </div>
    );
};

export default Wrapper;
