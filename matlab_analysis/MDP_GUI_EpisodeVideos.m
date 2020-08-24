function varargout = MDP_GUI_EpisodeVideos(varargin)
% MDP_GUI_EPISODEVIDEOS MATLAB code for MDP_GUI_EpisodeVideos.fig
%      MDP_GUI_EPISODEVIDEOS, by itself, creates a new MDP_GUI_EPISODEVIDEOS or raises the existing
%      singleton*.
%
%      H = MDP_GUI_EPISODEVIDEOS returns the handle to a new MDP_GUI_EPISODEVIDEOS or the handle to
%      the existing singleton*.
%
%      MDP_GUI_EPISODEVIDEOS('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MDP_GUI_EPISODEVIDEOS.M with the given input arguments.
%
%      MDP_GUI_EPISODEVIDEOS('Property','Value',...) creates a new MDP_GUI_EPISODEVIDEOS or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before MDP_GUI_EpisodeVideos_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to MDP_GUI_EpisodeVideos_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help MDP_GUI_EpisodeVideos

% Last Modified by GUIDE v2.5 22-Jul-2020 19:22:12

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @MDP_GUI_EpisodeVideos_OpeningFcn, ...
                   'gui_OutputFcn',  @MDP_GUI_EpisodeVideos_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

function SortEpisodes(handles)
global ParentFolderPath
chosenSimulation = handles.simulationmenu.Value;
chosenEntropyIndex = handles.entropymenu.Value;
chosenPredatorIndex = handles.predatormenu.Value;

filechosenPath = sprintf('%s/Data_NatComm/Simulation_%d/Occlusion_%d/Predator_%d/Depth_5000',...
    ParentFolderPath, chosenSimulation - 1, chosenEntropyIndex - 1, ...
    chosenPredatorIndex -1);
episodeFiles = dir(sprintf('%s/Episode_*', filechosenPath));

episodePaths = {};
for e = 1:length(episodeFiles)
    episodePaths = [strcat(episodeFiles(e).folder, '/', episodeFiles(e).name); episodePaths];
end

survivalEpisodeFiles = {};
deathEpisodeFiles = {};
for e = 1:length(episodePaths)
    episodeFile = episodePaths{e};
    fid = fopen(episodeFile);
    episode = textscan(fid, '%f %f %f %f %f %f %f', 'Delimiter', ',', 'HeaderLines', 1);
    fclose(fid);
    %episode = csvread(episodeFile, 1, 1);

    terminalReward = episode{end}(end);
    tokenizeFilePath = strsplit(episodeFile, '/');
    if terminalReward < -1
        deathEpisodeFiles = [tokenizeFilePath{end} deathEpisodeFiles];
    elseif terminalReward > 0
        survivalEpisodeFiles = [tokenizeFilePath{end} survivalEpisodeFiles];
    end
end

if isempty(survivalEpisodeFiles)
    survivalEpisodeFiles = {'0'};
elseif isempty(deathEpisodeFiles)
    deathEpisodeFiles = {'0'};
end

handles.survivalmenu.String = survivalEpisodeFiles;
handles.deathmenu.String = deathEpisodeFiles;

function occlusionCoordinates = GetOcclusionCoordinates(handles)
global ParentFolderPath
chosenSimulation = handles.simulationmenu.Value;
chosenEntropyIndex = handles.entropymenu.Value;
chosenPath = sprintf('%s/Data_NatComm/Simulation_%d/Occlusion_%d/OcclusionCoordinates.csv', ...
    ParentFolderPath, chosenSimulation - 1, chosenEntropyIndex - 1);

fid = fopen(chosenPath);
occlusionCoordinates = textscan(fid, '%f %f', 'Delimiter', ',', 'HeaderLines', 1);
fclose(fid);

function [agentTrajectory, predatorTrajectory, rewards] = GetEpisode(handles, condition)
global ParentFolderPath
chosenSimulation = handles.simulationmenu.Value;
chosenEntropyIndex = handles.entropymenu.Value;
chosenPredatorIndex = handles.predatormenu.Value;

if strcmp(condition, 'survival')
    contents = handles.survivalmenu.String;
    chosenPath = sprintf('%s/Data_NatComm/Simulation_%d/Occlusion_%d/Predator_%d/Depth_5000/%s', ...
        ParentFolderPath, chosenSimulation - 1, chosenEntropyIndex - 1,...
        chosenPredatorIndex - 1, contents{handles.survivalmenu.Value});
elseif strcmp(condition, 'death')
    contents = handles.deathmenu.String;
    chosenPath = sprintf('%s/Data_NatComm/Simulation_%d/Occlusion_%d/Predator_%d/Depth_5000/%s', ...
        ParentFolderPath, chosenSimulation-1, chosenEntropyIndex-1, ...
        chosenPredatorIndex - 1, contents{handles.deathmenu.Value});
end

fid = fopen(chosenPath);
episode = textscan(fid, '%f %f %f %f %f %f %f %f', 'Delimiter', ',', 'HeaderLines', 1);
fclose(fid);
agentTrajectory.X = episode{2};
agentTrajectory.Y = episode{3};
predatorTrajectory.X = episode{5};
predatorTrajectory.Y = episode{6};
rewards = episode{6};


function World = OccludeWorld(World, occlusionCoordinates)
occlusion.X = occlusionCoordinates{1};
occlusion.Y = occlusionCoordinates{2};
for j = 1:length(occlusion.Y)
    for i = 1:length(occlusion.X)
        World(occlusion.Y(i)+1, occlusion.X(i)+1) = 1;
    end
end

function WorldCopy = World2RGB(World, map)
WorldCopy = World;
zeroIndices = find(WorldCopy == 0);
oneIndices = find(WorldCopy == 1);
maxval = max(World(:));

World = floor((World./maxval)*length(map));
WorldCopy = ind2rgb(World, map);
[xZero, yZero] = ind2sub(size(WorldCopy), zeroIndices);
if ~isempty(oneIndices)
    [xOne, yOne] = ind2sub(size(WorldCopy), oneIndices);
    for indx = 1:length(xOne)
        WorldCopy(xOne(indx),yOne(indx), :) = [0 0 0];
    end
end
for indx = 1:length(xZero)
    WorldCopy(xZero(indx), yZero(indx), :) = [1 1 1];
end

function World = IntializeGridWorld(World, agentPositions, predatorPositions, occlusionCoordinates, handles)
World = OccludeWorld(World, occlusionCoordinates);

World(predatorPositions.Y(1)+1, predatorPositions.X(1)+1) = 3;
World(agentPositions.Y(1)+1, agentPositions.X(1)+1) = 2;
World(15,8) = 4;

gridworld_colormap = [0/255, 0/255, 0/255;
                      51/255, 125/255, 141/255;
                      214/255, 186/255, 62/255;
                      136/255, 35/255, 66/255];
%map = colormap;
map = gridworld_colormap;
WorldCopy = World2RGB(World, map);

h1 = image(handles.axes1, flipud(WorldCopy));
set(handles.axes1, 'Xtick', [], 'Ytick', []);

function Step(World, newAgentPosition, newPredatorPosition, handles)

World(newPredatorPosition.Y, newPredatorPosition.X) = 3;
World(newAgentPosition.Y, newAgentPosition.X) = 2;

gridworld_colormap = [0/255, 0/255, 0/255;
                      51/255, 125/255, 141/255;
                      214/255, 186/255, 62/255;
                      136/255, 35/255, 66/255];
%map = colormap;
map = gridworld_colormap;                  
WorldCopy = World2RGB(World, map);

image(handles.axes1, flipud(WorldCopy));
set(handles.axes1, 'Xtick', [], 'Ytick', []);

% --- Executes just before MDP_GUI_EpisodeVideos is made visible.
function MDP_GUI_EpisodeVideos_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to MDP_GUI_EpisodeVideos (see VARARGIN)

% Choose default command line output for MDP_GUI_EpisodeVideos
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes MDP_GUI_EpisodeVideos wait for user response (see UIRESUME)
% uiwait(handles.figure1);
global ParentFolderPath World XSize YSize

directory = pwd;
[ParentFolderPath] = fileparts(directory);
folderNames = utils.getAllSubFolders(ParentFolderPath);

numSimulations = 20;
%length(dir(strcat(ParentFolderPath, '/Data/'))) - 3;
numOcclusions = 10;
numPredators = 5;
XSize = 15;
YSize = 15;

World = zeros(XSize, YSize);

simulationList = string(0:numSimulations-1);
handles.simulationmenu.String = simulationList;
occlusionList = string(linspace(0, 0.9, numOcclusions));
handles.entropymenu.String = occlusionList;
predatorList = string(0:numPredators-1);
handles.predatormenu.String = predatorList;

% --- Outputs from this function are returned to the command line.
function varargout = MDP_GUI_EpisodeVideos_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in simulationmenu.
function simulationmenu_Callback(hObject, eventdata, handles)
% hObject    handle to simulationmenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns simulationmenu contents as cell array
%        contents{get(hObject,'Value')} returns selected item from simulationmenu
SortEpisodes(handles)


% --- Executes during object creation, after setting all properties.
function simulationmenu_CreateFcn(hObject, eventdata, handles)
% hObject    handle to simulationmenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in entropymenu.
function entropymenu_Callback(hObject, eventdata, handles)
% hObject    handle to entropymenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns entropymenu contents as cell array
%        contents{get(hObject,'Value')} returns selected item from entropymenu

SortEpisodes(handles)


% --- Executes during object creation, after setting all properties.
function entropymenu_CreateFcn(hObject, eventdata, handles)
% hObject    handle to entropymenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on selection change in predatormenu.
function predatormenu_Callback(hObject, eventdata, handles)
% hObject    handle to predatormenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns predatormenu contents as cell array
%        contents{get(hObject,'Value')} returns selected item from predatormenu
SortEpisodes(handles)


% --- Executes during object creation, after setting all properties.
function predatormenu_CreateFcn(hObject, eventdata, handles)
% hObject    handle to predatormenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on selection change in survivalmenu.
function survivalmenu_Callback(hObject, eventdata, handles)
% hObject    handle to survivalmenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns survivalmenu contents as cell array
%        contents{get(hObject,'Value')} returns selected item from survivalmenu

if strcmp(handles.survivalmenu.String, '0')
    return
end
global World XSize YSize M condition stop_state
condition = 1;
M = {};
discount = 0.98;
World = zeros(XSize, YSize);

occlusionCoordinates = GetOcclusionCoordinates(handles);
[agentPositions, predatorPositions, rewards] = GetEpisode(handles, 'survival');
terminalReward = rewards(end);
World = IntializeGridWorld(World, agentPositions, predatorPositions, occlusionCoordinates, handles);

if terminalReward > -1
    n = length(agentPositions.X);
else
    n = length(agentPositions.X);
end

World(predatorPositions.Y(1)+1, predatorPositions.X(1)+1) = 0;
World(agentPositions.Y(1)+1, agentPositions.X(1)+1) = 0;

steps(1) = 0;
discountedReward(1) = rewards(1);

M{1} = getframe(handles.axes1);
pause(0.1)
for indx = 2:n
    steps(indx) = steps(indx-1) + 1;
    discountedReward(indx) = discountedReward(indx-1) + rewards(indx)*discount;
    discount = discount * discount;
    
    newPredatorPosition.X = predatorPositions.X(indx) + 1;
    newPredatorPosition.Y = predatorPositions.Y(indx) + 1;
    
    newAgentPosition.X = agentPositions.X(indx) + 1;
    newAgentPosition.Y = agentPositions.Y(indx) + 1;
    if stop_state == 1
        stop_state = 0;
        break;
    end
    Step(World, newAgentPosition, newPredatorPosition, handles);
    M{indx} = getframe(handles.axes1);
    pause(0.1);
end


% --- Executes during object creation, after setting all properties.
function survivalmenu_CreateFcn(hObject, eventdata, handles)
% hObject    handle to survivalmenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in deathmenu.
function deathmenu_Callback(hObject, eventdata, handles)
% hObject    handle to deathmenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns deathmenu contents as cell array
%        contents{get(hObject,'Value')} returns selected item from deathmenu
if strcmp(handles.deathmenu.String, '0')
    return
end
global World XSize YSize M condition stop_state
M = {};
condition = 0;
discount = 0.98;
World = zeros(XSize, YSize);

occlusionCoordinates = GetOcclusionCoordinates(handles);
[agentPositions, predatorPositions, rewards] = GetEpisode(handles, 'death');
World = IntializeGridWorld(World, agentPositions, predatorPositions, occlusionCoordinates, handles);

steps(1) = 0;
discountedReward(1) = rewards(1);

n = length(agentPositions.X);

World(predatorPositions.Y(1)+1, predatorPositions.X(1)+1) = 0;
World(agentPositions.Y(1)+1, agentPositions.X(1)+1) = 0;

M{1} = getframe(handles.axes1);
pause(0.5);
for indx = 2:n
    steps(indx) = steps(indx-1) + 1;
    discountedReward(indx) = discountedReward(indx-1) + rewards(indx)*discount;
    discount = discount * discount;
    
    newPredatorPosition.X = predatorPositions.X(indx) + 1;
    newPredatorPosition.Y = predatorPositions.Y(indx) + 1;
    
    newAgentPosition.X = agentPositions.X(indx) + 1;
    newAgentPosition.Y = agentPositions.Y(indx) + 1;
    
    if stop_state == 1
        stop_state = 0;
        break;
    end
    Step(World, newAgentPosition, newPredatorPosition, handles); 
    
    M{indx} = getframe(handles.axes1);
    pause(0.1);
end

% --- Executes during object creation, after setting all properties.
function deathmenu_CreateFcn(hObject, eventdata, handles)
% hObject    handle to deathmenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in recordbutton.
function recordbutton_Callback(hObject, eventdata, handles)
% hObject    handle to recordbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global M condition ParentFolderPath
if condition == 1
    contents = handles.survivalmenu.String;
    episode = strsplit(contents{handles.survivalmenu.Value}, '.');
elseif condition == 0
    contents = handles.deathmenu.String;
    episode = strsplit(contents{handles.deathmenu.Value}, '.');
end
v = VideoWriter(sprintf('%s/Videos/Simulation%d_Occlusion%d_Predator%d_%s.mp4',... 
    ParentFolderPath, handles.simulationmenu.Value-1, handles.entropymenu.Value-1, handles.predatormenu.Value-1, episode{1}), 'MPEG-4');
%v.FileFormat = 'mp4';
v.FrameRate = 5;
open(v);
for i = 1:length(M)
    writeVideo(v, M{i});
end
close(v);
fprintf('video written\n')


% --- Executes on button press in nextbutton.
function nextbutton_Callback(hObject, eventdata, handles)
% hObject    handle to nextbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global condition 

if condition == 1
    currentEpisodeIndex = handles.survivalmenu.Value;
    handles.survivalmenu.Value = currentEpisodeIndex + 1;
    try
        survivalmenu_Callback(hObject, eventdata, handles);
    catch 
        handles.survivalmenu.Value = handles.survivalmenu.Value - 1;
        survivalmenu_Callback(hObject, eventdata, handles);
    end
elseif condition == 0
    currentEpisodeIndex = handles.deathmenu.Value;
    handles.deathmenu.Value = currentEpisodeIndex + 1;
    try
        deathmenu_Callback(hObject, eventdata, handles);
    catch
        handles.deathmenu.Value = handles.deathmenu.Value - 1;
        deathmenu_Callback(hObject, eventdata, handles);
    end

end

% --- Executes on button press in previousbutton.
function previousbutton_Callback(hObject, eventdata, handles)
% hObject    handle to previousbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global condition

if condition == 1
    currentEpisodeIndex = handles.survivalmenu.Value;
    nextEpisode = currentEpisodeIndex-1;
    if nextEpisode == 0
        nextEpisode = 1;
    end
    handles.survivalmenu.Value = nextEpisode;
    
    survivalmenu_Callback(hObject, eventdata, handles);
elseif condition == 0
    currentEpisodeIndex = handles.deathmenu.Value;
        nextEpisode = currentEpisodeIndex-1;
    if nextEpisode == 0
        nextEpisode = 1;
    end
    handles.deathmenu.Value = nextEpisode;
    
    deathmenu_Callback(hObject, eventdata, handles);
end


% --- Executes on button press in stopbutton.
function stopbutton_Callback(hObject, eventdata, handles)
% hObject    handle to stopbutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global stop_state
stop_state = 1;


% --- Executes on button press in replaybutton.
function replaybutton_Callback(hObject, eventdata, handles)
% hObject    handle to replaybutton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global condition
if condition == 1
    survivalmenu_Callback(hObject, eventdata, handles);
elseif condition == 0
    deathmenu_Callback(hObject, eventdata, handles);
end
