% -------------------------------------------------------------------------
% Parameters definition for maximumDrifts.m and any other variations
% -------------------------------------------------------------------------

prefDirs_NS_000_005.folder = 'data/archive/job21800/';
prefDirs_NS_000_005.jobNums = 21800:21899;
prefDirs_NS_000_005.title = '';
prefDirs_NS_000_005.preprocess = false;
prefDirs_NS_000_005.xlim = [-20 20];
prefDirs_NS_000_005.ylim = [-20 20];
prefDirs_NS_000_005.output = 'output/000_005_prefDirs_NS/maximumDrifts-21800-21899.eps';
prefDirs_NS_000_005.MarkerFaceColor = 'b';

% ----------------------------------------------------------------------------

Burak_Fiete_PrefDirs_000_001.folder = 'data/000_001_Burak_Fiete_PrefDirs/';
Burak_Fiete_PrefDirs_000_001.jobNums = 40000:40099;
Burak_Fiete_PrefDirs_000_001.title = '';
Burak_Fiete_PrefDirs_000_001.preprocess = false;
Burak_Fiete_PrefDirs_000_001.xlim = [-20 20];
Burak_Fiete_PrefDirs_000_001.ylim = [-20 20];
Burak_Fiete_PrefDirs_000_001.output = 'output/000_001_Burak_Fiete_PrefDirs/maximumDrifts-40000-40099.eps';
Burak_Fiete_PrefDirs_000_001.MarkerFaceColor = 'b';

% ----------------------------------------------------------------------------

bump_initialized_002.folder = 'data/002_bump_initialized/';
bump_initialized_002.jobNums = 2100:2199;
bump_initialized_002.title = '';
bump_initialized_002.preprocess = false;
bump_initialized_002.xlim = [-20 20];
bump_initialized_002.ylim = [-20 20];
bump_initialized_002.output = 'output/002_bump_initialized/maximumDrifts-2100-2199.eps';
bump_initialized_002.MarkerFaceColor = 'b';

% ----------------------------------------------------------------------------

timeNoise_noInitNoise_003.sigma_0_1.folder = 'data/003_timeNoise_noInitNoise/sigma_0_1/';
timeNoise_noInitNoise_003.sigma_0_1.jobNums = 20200:20299;
timeNoise_noInitNoise_003.sigma_0_1.title = '';
timeNoise_noInitNoise_003.sigma_0_1.preprocess = false;
timeNoise_noInitNoise_003.sigma_0_1.xlim = [-10 10];
timeNoise_noInitNoise_003.sigma_0_1.ylim = [-10 10];
timeNoise_noInitNoise_003.sigma_0_1.output = 'output/003_timeNoise_noInitNoise/noise_sigma_0_1-maximumDrifts.eps';
timeNoise_noInitNoise_003.sigma_0_1.MarkerFaceColor = 'b';

timeNoise_noInitNoise_003.sigma_0_2.folder = 'data/003_timeNoise_noInitNoise/sigma_0_2/';
timeNoise_noInitNoise_003.sigma_0_2.jobNums = 20300:20399;
timeNoise_noInitNoise_003.sigma_0_2.title = '';
timeNoise_noInitNoise_003.sigma_0_2.preprocess = false;
timeNoise_noInitNoise_003.sigma_0_2.xlim = [-10 10];
timeNoise_noInitNoise_003.sigma_0_2.ylim = [-3 3];
timeNoise_noInitNoise_003.sigma_0_2.output = 'output/003_timeNoise_noInitNoise/noise_sigma_0_2-maximumDrifts.eps';
timeNoise_noInitNoise_003.sigma_0_2.MarkerFaceColor = 'b';

% ----------------------------------------------------------------------------

NoisyNetwork_NoPrefDirs_004.sigma_0_1.folder = 'data/004_NoisyNetwork_NoPrefDirs/correction_l0/sigma_0_1/';
NoisyNetwork_NoPrefDirs_004.sigma_0_1.jobNums = 30000:30099;
NoisyNetwork_NoPrefDirs_004.sigma_0_1.title = '';
NoisyNetwork_NoPrefDirs_004.sigma_0_1.preprocess = false;
NoisyNetwork_NoPrefDirs_004.sigma_0_1.xlim = [-10 10];
NoisyNetwork_NoPrefDirs_004.sigma_0_1.ylim = [-3 3];
NoisyNetwork_NoPrefDirs_004.sigma_0_1.output = 'output/004_NoisyNetwork_NoPrefDirs/correction_l0/noise_sigma_0_1-maximumDrifts.eps';
NoisyNetwork_NoPrefDirs_004.sigma_0_1.MarkerFaceColor = 'b';

NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.folder = 'data/004_NoisyNetwork_NoPrefDirs/correction_l0/init_cond_transposed/sigma_0_1/';
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.jobNums = 40000:40099;
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.title = '';
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.preprocess = false;
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.xlim = [-3 3];
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.ylim = [-10 10];
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.output = 'output/004_NoisyNetwork_NoPrefDirs/correction_l0/init_cond_transposed/noise_sigma_0_1-maximumDrifts.eps';
NoisyNetwork_NoPrefDirs_004.transp.sigma_0_1.MarkerFaceColor = 'b';

% ----------------------------------------------------------------------------

StartFromEL_006.lambda_net_20.folder = 'data/006_StartFromEL/lambda_net_20';
StartFromEL_006.lambda_net_20.jobNums = 30100:30199;
StartFromEL_006.lambda_net_20.title = '';
StartFromEL_006.lambda_net_20.preprocess = false;
StartFromEL_006.lambda_net_20.xlim = [-20 20];
StartFromEL_006.lambda_net_20.ylim = [-20 20];
StartFromEL_006.lambda_net_20.output = 'output/006_StartFromEL/lambda_net_20-maximumDrifts.eps';
StartFromEL_006.lambda_net_20.lambda_net = 20;
StartFromEL_006.lambda_net_20.MarkerFaceColor = 'b';

SpacingDrifts_009.lambda_net_13.folder = 'data/009_SpacingDrifts/lambda_net_13/';
SpacingDrifts_009.lambda_net_13.jobNums = 90000:90099;
SpacingDrifts_009.lambda_net_13.title = '';
SpacingDrifts_009.lambda_net_13.preprocess = false;
SpacingDrifts_009.lambda_net_13.xlim = [-10 10];
SpacingDrifts_009.lambda_net_13.ylim = [-10 10];
SpacingDrifts_009.lambda_net_13.output = 'output/009_SpacingDrifts/lambda_net_13-maximumDrifts.eps';
SpacingDrifts_009.lambda_net_13.lambda_net = 13;
SpacingDrifts_009.lambda_net_13.MarkerFaceColor = 'b';

SpacingDrifts_009.lambda_net_14.folder = 'data/009_SpacingDrifts/lambda_net_14/';
SpacingDrifts_009.lambda_net_14.jobNums = 90100:90199;
SpacingDrifts_009.lambda_net_14.title = '';
SpacingDrifts_009.lambda_net_14.preprocess = false;
SpacingDrifts_009.lambda_net_14.xlim = [-10 10];
SpacingDrifts_009.lambda_net_14.ylim = [-10 10];
SpacingDrifts_009.lambda_net_14.output = 'output/009_SpacingDrifts/lambda_net_14-maximumDrifts.eps';
SpacingDrifts_009.lambda_net_14.lambda_net = 14;
SpacingDrifts_009.lambda_net_14.MarkerFaceColor = 'b';

SpacingDrifts_009.lambda_net_16.folder = 'data/009_SpacingDrifts/lambda_net_16/';
SpacingDrifts_009.lambda_net_16.jobNums = 90200:90299;
SpacingDrifts_009.lambda_net_16.title = '';
SpacingDrifts_009.lambda_net_16.preprocess = false;
SpacingDrifts_009.lambda_net_16.xlim = [-10 10];
SpacingDrifts_009.lambda_net_16.ylim = [-10 10];
SpacingDrifts_009.lambda_net_16.output = 'output/009_SpacingDrifts/lambda_net_16-maximumDrifts.eps';
SpacingDrifts_009.lambda_net_16.lambda_net = 16;
SpacingDrifts_009.lambda_net_16.MarkerFaceColor = 'b';

SpacingDrifts_009.lambda_net_18.folder = 'data/009_SpacingDrifts/lambda_net_18/';
SpacingDrifts_009.lambda_net_18.jobNums = 90300:90399;
SpacingDrifts_009.lambda_net_18.title = '';
SpacingDrifts_009.lambda_net_18.preprocess = false;
SpacingDrifts_009.lambda_net_18.xlim = [-10 10];
SpacingDrifts_009.lambda_net_18.ylim = [-10 10];
SpacingDrifts_009.lambda_net_18.output = 'output/009_SpacingDrifts/lambda_net_18-maximumDrifts.eps';
SpacingDrifts_009.lambda_net_18.lambda_net = 18;
SpacingDrifts_009.lambda_net_18.MarkerFaceColor = 'b';

% -------------------------------------------------------------------------
% End parameters
% -------------------------------------------------------------------------