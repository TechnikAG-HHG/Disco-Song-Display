import { useState, useEffect, useRef } from 'react';
import '../index.css';
import { io, Socket } from 'socket.io-client';

interface VisualizerBarProps {
    id: number;
    initialHeight?: number;
}

function VisualizerBar({ id, initialHeight = 350 }: VisualizerBarProps) {
    const [barHeight, setBarHeight] = useState(initialHeight);
    const socketRef = useRef<Socket | null>(null);

    useEffect(() => {
        // Create Socket.IO connection to the main namespace
        socketRef.current = io('http://localhost:5000');

        // Register this component for a specific bar
        socketRef.current.on('connect', () => {
            console.log(`Socket.IO connection established for bar ${id}`);
            socketRef.current?.emit('register_bar', { bar_id: id });
        });

        // Listen for bar_update events
        socketRef.current.on('bar_update', (data) => {
            // Only update if this event is for our bar
            if (data.bar_id === id) {
                setBarHeight(data.height);
            }
        });

        // Connection status logging
        socketRef.current.on('connect_error', (error) => {
            console.error(`Socket.IO connection error for bar ${id}:`, error);
        });

        // Clean up Socket.IO connection on component unmount
        return () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };
    }, [id]);

    return (
        <>
            <div
                className="bar bg-black w-7 mr-1 rounded-2xl"
                style={{
                    height: `${barHeight}px`,
                    transition: 'height 0.1s ease-in-out',
                }}
                id={`bar-${id}`}
            ></div>
        </>
    );
}

export default VisualizerBar;
