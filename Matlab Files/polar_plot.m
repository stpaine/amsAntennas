function [ X ] = polar_plot( File_Name,Increments,Lines,Zero,SLL )
%This function draws a polar diagram from the antenna data (.csv)

% VERSION 2.5, 17/01/2016

%Example input polar_plot('H-Pol Elevation.csv',1,1,1,0)

%First 1 is for the number of increments i.e. 1 deg, 2 deg etc
%To insert lines, use a 1, to remove, use anything else
%Use the Zero function, set to 1, to center the data
%sometimes wont work if data is too skewed to one side.
%last input argument is for labelling the SLL points

%If the dynamic range on the Polar plot is too high change the mask from
%"pad" to the appropriate value

%I have updated the Dirplot scaling such tahat it goes from -50 to 0.
%To change this, simply go to the bottom of the Dirplot file and edit it

%Takes in the increments in degrees i.e. 2 degree increments
%NOTE: CAN ONLY TAKE IN DEGREES THAT DIVIDE INTO 180! (1,2,3,4,5,6,9,10,12)

%takes in a column matrix csv file
%once file is read, convert the column matrix into a single column
A=csvread(File_Name);
B=A(:,1);
C=B' - max(B'); %normalise to zero
% This pads the mask. Needs to be a multiple of 5 to fit properly on polar plot
pad=round(min(C)/5)*5;
% Normalise the graph such that the peak value is at 0 degrees
index=find(C==max(C));
% Break vector into 2 so that we can add to each side equally
Left_side=C(1:index-1);%Left side of matrix
Right_side=C(index+1:end);%Right side of matrix

if Zero == 1
    if length(Left_side)+length(Right_side)<359;
        while length(Left_side)<(180/Increments); %Fill left side of matrix with 180 elements
            Left_side=[pad Left_side]; %set the level to something moderate - change accordingly
        end
        
        while length(Right_side)<((180-Increments)/Increments); %Fill right side of matrix with 180 elements
            Right_side=[Right_side pad]; %set the level to something moderate - change accordingly
        end
    end
    radiation_pattern=[Left_side max(C)];
    radiation_pattern=[radiation_pattern Right_side];
else
    C_new = C;
    while length(C_new)<360/Increments;
        C_new=[C_new pad];
    end
    radiation_pattern=C_new;
end

theta=-180:Increments:179;
%plots main polar plot
try
    modified_dirplot(theta,radiation_pattern,'b')
    title('Polar Plot of Antenna Radiation Pattern')
    hold on
    
    %create a new theta such that we can overwrite the "false" additions that were added to the matrix above
    mask=[];
    for i=1:Increments:360;
        mask=[mask pad];
    end
    modified_dirplot(theta,mask,'k')
    % modified_dirplot((find(abs(radiation_pattern+3)==min(abs(Right_side+3)))),-(min(abs(Right_side+3)))-3,'xk')
    % modified_dirplot((find(abs(radiation_pattern+3)==min(abs(Left_side+3)))),-(min(abs(Left_side+3)))-3,'xk')
    hold off
catch
    message=('Antenna polar plot: Error trying to zero plot, please try use un-zeroed mode');
    disp(message)
end

% Half power points and beamwidth
% try
    figure(2);
    x_axis=0:Increments:(length(C)-1)*Increments;
    plot(x_axis,C)
    xlim([0 length(radiation_pattern)-1]);
    title('Antenna Radiation Pattern')
    xlabel('Angle [Degrees]')
    ylabel('Normalised Gain [dBi]')
    HP_Left=min(abs(Left_side+3));
    HP_Right=min(abs(Right_side+3));
    hold on
    grid on
    V=find(abs(C+3)==HP_Right);
    Z=find(abs(C+3)==HP_Left);
    
    % Finding the best approximated 3dB point (Right)
    x1=x_axis(V);
    y1=C(V);
    x2=x_axis(V+1);
    y2=C(V+1);
    m=(y1-y2)/(x1-x2); %getting the gradient
    c=y1-m*x1; %getting the equation for the straght line
    x_Right=(-3-c)/m; %getting the -3dB point
    
    % Finding the best approximated 3dB point (Left)
    x1=x_axis(Z);
    y1=C(Z);
    x2=x_axis(Z-1);
    y2=C(Z-1);
    m=(y1-y2)/(x1-x2); %getting the gradient
    c=y1-m*x1; %getting the equation for the straght line
    x_Left=(-3-c)/m; %getting the -3dB point
    
    % This is for when the code creates two left and two right 3dB points
%   % I am not sure why this occurs  
    if length(x_Left)>1;
        x_Right_corrected=(x_Right(1)+x_Left(1))/2;
        x_Left_corrected=(x_Right(2)+x_Left(2))/2.0001;
        HPBW=abs(x_Right_corrected - x_Left_corrected);
        
        % Plot the results
        plot(x_Right_corrected,-3,'xk')
        plot(x_Left_corrected,-3,'xk')

    else
        HPBW=abs(x_Right - x_Left);
    
        % Plot the results
        plot(x_Right,-3,'xk')
        plot(x_Left,-3,'xk')
    end 

    if Lines == 1;
        line('XData', [x_Right x_Right x_Right], 'YData', [0 -6 0], 'LineWidth', 0.4, ...
            'LineStyle', '-.', 'Color', [0.5 0.5 0.5])
        line('XData', [x_Left x_Left x_Left], 'YData', [0 -6 0], 'LineWidth', 0.4, ...
            'LineStyle', '-.', 'Color', [0.5 0.5 0.5])
    end
    % text(x_Left-12*abs((Increments/4-5/4)),-3.6,[num2str(x_Left) ' Deg']);
    text(6/Increments,-2,['HPBW = ' num2str(HPBW) ' degrees']);
    % text(x_Right+abs((Increments/4-5/4)),-4.3,[num2str(x_Right) ' Deg']);

    % Calculating the SLL
    all_peaks=findpeaks(C);
    first_peak=find(all_peaks==max(all_peaks));
    SLL_Left=max(all_peaks(1:first_peak-1));
    SLL_Right=max(all_peaks(first_peak+1:end));
    
    position_SL=find(C==SLL_Left);
    position_SR=find(C==SLL_Right);

    % Plot the position of the side lobes as an overlay
%   This has a big bug, when equal SLL the thing bombs out
    if SLL==1
        if SLL_Left==SLL_Right
            plot(position_SL*(Increments)-Increments,SLL_Left,'xk')
    %         text(position_SL*(Increments)-Increments+3/Increments,SLL_Left,[num2str(SLL_Left) ' dB']);
            plot(position_SR*(Increments)-Increments,SLL_Right,'xk')
    %         text(position_SR*(Increments)-Increments+3/Increments,SLL_Right,[num2str(SLL_Right) ' dB']);

        else
            plot(position_SL*(Increments)-Increments,SLL_Left,'xk')
            text(position_SL*(Increments)-Increments+3/Increments,SLL_Left,[num2str(SLL_Left) ' dB']);
            plot(position_SR*(Increments)-Increments,SLL_Right,'xk')
            text(position_SR*(Increments)-Increments+3/Increments,SLL_Right,[num2str(SLL_Right) ' dB']);
        end
    else
        plot(position_SL*(Increments)-Increments,SLL_Left,'xk')
%       text(position_SL*(Increments)-Increments+3/Increments,SLL_Left,[num2str(SLL_Left) ' dB']);
        plot(position_SR*(Increments)-Increments,SLL_Right,'xk')
%       text(position_SR*(Increments)-Increments+3/Increments,SLL_Right,[num2str(SLL_Right) ' dB']);
    end
    hold off
    grid off
    % Determine which one is the bigger one
    if SLL_Left>SLL_Right;
        SLL=SLL_Left;
    else;
        SLL=SLL_Right;
    end
    
    text(6/Increments,-4.5,['SLL = ' num2str(SLL) ' dB']);
% catch
%     message=('Antenna pattern plot: Not enough data to plot side lobes correctly');
%     disp(message)
end