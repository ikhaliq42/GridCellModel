cells_per = 2; experiment = 4; trial_no = 2; inc_border = 1; inc_place = 0;

path = sprintf('sim_bump_test_%i_cells/experiment_%i/',cells_per,experiment);
filename = sprintf('BumpParams_trial%i.mat',trial_no);
h5filename = 'job00000_output.h5';
load(strcat(path,filename));

if inc_border 
    h5dataPath = sprintf('/trials/%i/connections/B->E',trial_no);
    conns = h5read(strcat(path,h5filename),h5dataPath);
    cells_per = 1;
end
  
step_size = 500; res = 1;

for tbin = 1:step_size:size(params.mu_x, 2)-step_size
    mu_x      = params.mu_x(tbin);
    mu_y      = params.mu_y(tbin);
    sigma  = abs(params.sigma(tbin));
    x = 0:res:33; y = 0:res:29;
    [X, Y]  = meshgrid(x,y);
    Z      = mvnpdf([X(:) Y(:)],[mu_x mu_y],[sigma 0; 0 sigma]);
    Z      = reshape(Z,length(y),length(x));    
    contour(X,Y,Z);
    if inc_border        
        target = reshape(conns(1,:),34,30)';
        hold on; contour(X,Y,target); hold off;
         for n = 1:cells_per:size(conns,1)
             target = reshape(conns(n,:),34,30)';
             hold on; contour(X,Y,target); hold off;
         end
    end
    title(sprintf('Bump Position: t = %i ms',tbin));
    axis([0 34 0 30]);
    pause(0.1);
end

