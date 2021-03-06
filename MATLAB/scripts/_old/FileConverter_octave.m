close all
clear all
%--------------------------------------------------------------------------
%   EEG to MAT File Converter
%   Author : Simon Kojima
%   Version : 3
%--------------------------------------------------------------------------
%   Settings

EEGFileName = '20181127_B36_Stream_';
FileNumber = 7;

%--------------------------------------------------------------------------

for l=1:FileNumber
   
    FileNumberString = num2str(l);
    
    for m=1:4-length(FileNumberString)
        FileNumberString = strcat(num2str(0),FileNumberString);
    end
    
    printf(FileNumberString)
    
    Data = bva_loadeeg(strcat(strcat(EEGFileName,FileNumberString),'.vhdr'));
    Trigger = bva_readmarker(strcat(strcat(EEGFileName,FileNumberString),'.vmrk'));
    [Fs,Label] = bva_readheader(strcat(strcat(EEGFileName,FileNumberString),'.vhdr'));
    
    ConvertedData.data = double(Data);

    ConvertedTriggerData = zeros(1,size(Data,2));
    
    for m=1:size(Trigger,2)
        ConvertedTriggerData(Trigger(2,m)) = Trigger(1,m);
    end
    
    ConvertedData.trig = ConvertedTriggerData;
    
    Data = ConvertedData.data;
    Trigger = ConvertedData.trig;
    
    Time = 1/Fs:1/Fs:size(Data,2)/Fs;
    
    save(strcat(strcat(EEGFileName,FileNumberString),'.mat'),'Data','Trigger','Time','Fs','Label','-v7');
    
end

fprintf('Completed !!\n');