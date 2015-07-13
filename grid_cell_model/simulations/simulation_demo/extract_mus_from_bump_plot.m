path = 'output_dir/demo_output_data/';
num_trials = 1;
mu_x = [];
mu_y = [];
for i = 0:num_trials-1
    load(strcat(path,sprintf('BumpParams_trial%i.mat',i)));
    mu_x = [mu_x params.mu_x'];
    mu_y = [mu_y params.mu_y'];
    clear params
end


save('-mat-binary',strcat(path,sprintf('mu_vals.mat')));
