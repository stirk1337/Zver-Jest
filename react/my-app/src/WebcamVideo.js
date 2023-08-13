import React, { useCallback, useRef, useState } from "react";
import Webcam from "react-webcam";
import axios from 'axios';
import { useEffect } from "react";

export default function WebcamVideo(props) {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [text, setText] = useState('')
  const [isStopped, setStop] = useState(false)
  const [swapper, setSwapper] = useState('Язык жестов')
  let isActive = false
  const handleDataAvailable = useCallback(
    ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks((prev) => prev.concat(data));
      }
      let arrayData = []
      arrayData.push(data)
      const blob = new Blob(arrayData, {
        type: "video/webm",
      });
      const url = URL.createObjectURL(blob);
        axios({
            method: 'get',
            url: url, // 'http://100.73.214.19:8000/get_transcribe'
            responseType: 'blob'
        }).then(function(response){
            var reader = new FileReader();
            reader.readAsDataURL(response.data); 
            reader.onloadend = function() {
                var base64data = reader.result;
                console.log(base64data)
                var bodyFormData = new FormData();
                bodyFormData.append('filename', 'video');
                bodyFormData.append('filedata', base64data); 
                console.log(bodyFormData)
                axios({
                    method: "post",
                    url: "http://100.73.214.19:8000/upload",
                    data: bodyFormData,
                    headers: { "Content-Type": "multipart/form-data" },
                })
                .then(function (response) {
                    if(response.data !== 'Nothing, bro'){
                        console.log(response.data)
                        setText((prev) => prev + ' ' + response.data.additional_response);
                            let url = 'http://100.73.214.19:8000/download_mp3/' + response.data.audio_response;
                            let audio = new Audio();
                            audio.src = url
                            audio.autoplay = true;
                    }
                })
                .catch(function (error) {
                    console.log(error);
                });
            }
        })
    },
    [setRecordedChunks]
  );

    function handleStartCaptureClick() {
    setStop(false)
    setCapturing(true);
    mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
      mimeType: "video/webm",
    });
    mediaRecorderRef.current.addEventListener(
      "dataavailable",
      handleDataAvailable
    );
    mediaRecorderRef.current.start();
    startLoop()
  };

  function startLoop(){
    if(!isActive){
        isActive = true
        const interval = setInterval(() => {
            console.log('uwu')
            if(mediaRecorderRef.current.state !== 'inactive'){
                handleStopCaptureClick()
                handleStartCaptureClick()
            }
            else{
                props.AddHistory(document.querySelector('.guest-text').textContent)
                clearInterval(interval)
            }
            return () => clearInterval(interval);
          }, 7000);
    }

  }

  function handleStopCaptureClick(){
    if(mediaRecorderRef.current.state !== 'inactive'){
        setStop(true)
        mediaRecorderRef.current.stop();
        setCapturing(false);
    }
  };

  const videoConstraints = {
    width: 420,
    height: 420,
    facingMode: "user",
  };

  function handleSwapperClick(){
    console.log('dddd')
    if(swapper === 'Дактилология'){
        setSwapper('Язык жестов')
    }
    else{
        setSwapper('Дактилология')
    }
  }

  return (
    <div className="Container hidden">
        <div className="swapper">
            <p className="diaktology">{swapper}</p>
            <img src="swapper.svg" alt="смена режима" onClick={handleSwapperClick}></img>
        </div>
      <Webcam
        height={400}
        width={400}
        audio={false}
        mirrored={true}
        ref={webcamRef}
        videoConstraints={videoConstraints}
      />
      {capturing ? (
        <img src="startGuesting-icon.svg" alt="старт" className="start active" onClick={handleStopCaptureClick}></img>
      ) : (
        <img src="startGuesting-icon.svg" alt="старт" className="start" onClick={handleStartCaptureClick}></img>
      )}
      <p className="guest-text">{text}</p>
    </div>
  );
}