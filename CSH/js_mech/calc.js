
//var math = mathjs();

function calcjs() {

	var processScope = function(scope) {
		var finalModel = {};
		
		_.each(scope, function(m) {
			var name = m.get('name');
			
			var finalModelName = name;
			
			var startsWithDigitRe = /^\d/;
			if (startsWithDigitRe.test(name)) {
				finalModelName = "MSID_" + name;
			}
						
			var raw_val = m.get('value');
			
			var final_val = raw_val;
			
			if (raw_val !== null) {				
				final_val = Number(raw_val);
			}

			finalModel[finalModelName] = final_val;				
		});
		
		return finalModel;
	};
	
	var nullCheck = function(scope) {
		var hasNull = false;
		
		_.each(scope, function(m) {			
			if (m === null) {
				hasNull = true;
			}
		});
		
		return hasNull;
	};
	
	var convertBitrate = function(raw_val) {
		var final_val = null;
		
		if (raw_val === '8') {
			final_val = Number(raw_val);
		} else if (raw_val === "1024") {
			final_val = 1024000;
		} else if (raw_val.slice(-1) === 'K') {
			var tempStr = raw_val.substring(0, raw_val.length - 1);
			final_val = Number(tempStr) * 1000;
		}
		
		return final_val;
	}
	
	var calcs = {};

	// MCALC     SA_ANG 1S IEQN AOSARES1/2 + AOSARES2/2
	// MLIMIT  SET 0 DEFAULT PPENG  46  46.1  170.2  179 (F_MAIN)
	calcs.SA_ANG = function() {
		var msidList = ['AOSARES1', 'AOSARES2'];
		var mnffreq = 32;
			
		var SA_ANG = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('(AOSARES1 / 2) + (AOSARES2 / 2)');
			return eqn.compile().eval(scope);
		}

		SA_ANG.transform = function(args, math, scope) {
			return SA_ANG(processScope(scope));
		}

		math.import({
			SA_ANG: SA_ANG
		});

		SA_ANG.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},


			run: function(scope) {
				return math.eval('SA_ANG()', scope);
			}
		}
	}();

	// FIXME: This should NOT be a calc
	// MCALC     FSS_ROLL 1S IEQN AOALPANG*1
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE SUN PPENG   -20 -15 15 20 
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NSUN PPENG  -1000 -1000 1000 1000
	// MLIMSW    AOSUNPRS 
	calcs.FSS_ROLL = function() {
		var msidList = ['AOALPANG'];
		var mnffreq = 32;
		
		var FSS_ROLL = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AOALPANG');
			return eqn.compile().eval(scope);
		}   	

		FSS_ROLL.transform = function(args, math, scope) {
			return FSS_ROLL(processScope(scope));
		}

		math.import({
			FSS_ROLL: FSS_ROLL
		});

		FSS_ROLL.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('FSS_ROLL()', scope);
			}
		}	
	}();

	// MCALC     FSS_PITCH 1S IEQN 90 - AOBETANG*1
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE SUN PPENG  45  45  140  140
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NSUN PPENG  -1000 -1000 1000 1000 
	// MLIMSW    AOSUNPRS
	calcs.FSS_PITCH = function() {
		var msidList = ['AOBETANG'];
		var mnffreq = 32;

		var FSS_PITCH = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('90 - AOBETANG');
			return eqn.compile().eval(scope);
		}   	

		FSS_PITCH.transform = function(args, math, scope) {
			return FSS_PITCH(processScope(scope));
		}

		math.import({
			FSS_PITCH: FSS_PITCH
		});

		FSS_PITCH.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('FSS_PITCH()', scope);
			}
		}
	}();

	// MCALC POWER            1S IEQN ELBI_LOW * ELBV
	// MLIMIT  SET 0 DEFAULT PPENG 350.0 350.0 1800.0 1800.0
	calcs.POWER = function() {
		var msidList = ['ELBI_LOW', 'ELBV'];
		var mnffreq = 32;

		var POWER = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('ELBI_LOW * ELBV');
			return eqn.compile().eval(scope);
		}   	

		POWER.transform = function(args, math, scope) {
			return POWER(processScope(scope));
		}

		math.import({
			POWER: POWER
		});

		POWER.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('POWER()', scope);
			}
		}
	}();

	// FIXME - MSIDs beginning with a number are a problem - interpreted as the number
	// times rest of string. Temporary fix here.

	// MCALC   EVENT_A    2S  IEQN   ( 2DETART  / 255.0 ) - 1.0
	// MLIMIT  SET 0 DEFAULT PPENG -1.0 -1.0 10 30
	calcs.EVENT_A = function() {
		var msidList = ['2DETART'];
		var mnffreq = 16;
		
		var EVENT_A = function(scope) {	
			if (nullCheck(scope) == true) {
				return null;
			}
			
			// Note: MATH doesn't like components that begin
			// with a number, so processScope appends MSID_ to such
			// MSIDs
			var eqn = math.parse('(MSID_2DETART - 255.0) - 1.0');

			return eqn.compile().eval(scope);
		}   	

		EVENT_A.transform = function(args, math, scope) {
			return EVENT_A(processScope(scope));
		}

		math.import({
			EVENT_A: EVENT_A
		});

		EVENT_A.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('EVENT_A()', scope);
			}
		}
	}();

	// FIXME - MSIDs beginning with a number are a problem - interpreted as the number
	// times rest of string. Temporary fix here.

	// MCALC   SHIELD_A    2S  IEQN   ( 2SHLDART  / 255.0 ) - 1.0
	// MLIMIT  SET 0 DEFAULT PPENG -1.0 -1.0 80 245   
	calcs.SHIELD_A = function() {
		var msidList = ['2SHLDART'];
		var mnffreq = 16;

		var SHIELD_A = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			// Note: MATH doesn't like components that begin
			// with a number, so processScope appends MSID_ to such
			// MSIDs

			var eqn = math.parse('(MSID_2SHLDART / 255.0) - 1.0');

			return eqn.compile().eval(scope);
		}   	

		SHIELD_A.transform = function(args, math, scope) {
			return SHIELD_A(processScope(scope))
		}

		math.import({
			SHIELD_A: SHIELD_A
		});

		SHIELD_A.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SHIELD_A()', scope);
			}
		}
	}();

	// MCALC   EARTH_RADIUS 1S IEQN 1*6378
	// AXAF_RANGE 1S IEQN SQRT(AOSCPOS1^2 + AOSCPOS2^2 + AOSCPOS3^2)- EARTH_RADIUS
	calcs.AXAF_RANGE = function() {
		var msidList = ['AOSCPOS1', 'AOSCPOS2', 'AOSCPOS3'];
		var mnffreq = 32;

		var AXAF_RANGE = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('sqrt(AOSCPOS1^2 + AOSCPOS2^2 + AOSCPOS3^2) - 6378');
			return eqn.compile().eval(scope);
		}   	

		AXAF_RANGE.transform = function(args, math, scope) {
			return AXAF_RANGE(processScope(scope));
		}

		math.import({
			AXAF_RANGE: AXAF_RANGE
		});

		AXAF_RANGE.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('AXAF_RANGE()', scope);
			}
		}	
	}();    

	calcs.GCA_6RATE1 = function() {
		var msidList = ['6RATE1'];
		var mnffreq = 32;

		var GCA_6RATE1 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('MSID_6RATE1');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}

		GCA_6RATE1.transform = function(args, math, scope) {
			return GCA_6RATE1(processScope(scope));
		}

		math.import({
			GCA_6RATE1: GCA_6RATE1
		});

		GCA_6RATE1.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('GCA_6RATE1()', scope);
			}
		}

	}();

	calcs.GCA_6RATE2 = function() {
		var msidList = ['6RATE2'];
		var mnffreq = 32;

		var GCA_6RATE2 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('MSID_6RATE2');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}

		GCA_6RATE2.transform = function(args, math, scope) {
			return GCA_6RATE2(processScope(scope));
		}

		math.import({
			GCA_6RATE2: GCA_6RATE2
		});

		GCA_6RATE2.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('GCA_6RATE2()', scope);
			}
		}
	}();

	calcs.GCA_6RATE3 = function() {
		var msidList = ['6RATE3'];
		var mnffreq = 32;

		var GCA_6RATE3 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('MSID_6RATE3');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}

		GCA_6RATE3.transform = function(args, math, scope) {
			return GCA_6RATE3(processScope(scope));
		}

		math.import({
			GCA_6RATE3: GCA_6RATE3
		});

		GCA_6RATE3.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('GCA_6RATE3()', scope);
			}
		}
	}();

	// MCALC     CSS_ROLL 1S IEQN ATAN( (-1*AOSUNSA2) / (-1*AOSUNSA3) ) * 180.0 / 3.14159
	// MLIMIT  SET 0 DEFAULT PPENG -20 -15 15 20
	calcs.CSS_ROLL = function() {
		var msidList = ['AOSUNSA2', 'AOSUNSA3'];
		var mnffreq = 32;

		var CSS_ROLL = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('atan( (-1 * AOSUNSA2) / (-1 * AOSUNSA3) )');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}


		CSS_ROLL.transform = function(args, math, scope) {
			return CSS_ROLL(processScope(scope));
		}

		math.import({
			CSS_ROLL: CSS_ROLL
		});

		CSS_ROLL.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('CSS_ROLL()', scope);
			}
		}
	}();

	// MCALC     CSS_PITCH 1S IEQN 90.0 - ACOS(AOSUNSA1 * 1.0) * 180.0 / 3.14159
	// MLIMIT  SET 0 DEFAULT PPENG -20 -5 5 20
	calcs.CSS_PITCH = function() {
		var msidList = ['AOSUNSA1'];
		var mnffreq = 32;

		var CSS_PITCH = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('acos(AOSUNSA1)');
			return (90 - math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg'));
		}

		CSS_PITCH.transform = function(args, math, scope) {
			return CSS_PITCH(processScope(scope));
		}

		math.import({
			CSS_PITCH: CSS_PITCH
		});

		CSS_PITCH.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('CSS_PITCH()', scope);
			}
		}
	}();

	// MCALC   RATE_ROLL 1S IEQN AORATE1 * 3600.0 * 180.0 / 3.14159
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE NPNT PPENG  -10 -4 4 10
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NMAN PPENG  -300 -271 271 300
	// MLIMIT    SET 2 DEFAULT  SWITCHSTATE NSUN PPENG  -400 -360 360 400
	// MLIMSW    AOPCADMD
	calcs.RATE_ROLL = function() {
		var msidList = ['AORATE1'];
		var mnffreq = 32;
		
		var RATE_ROLL = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORATE1');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		RATE_ROLL.transform = function(args, math, scope) {
			return RATE_ROLL(processScope(scope));
		}

		math.import({
			RATE_ROLL: RATE_ROLL
		});

		RATE_ROLL.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RATE_ROLL()', scope);
			}
		}

	}();

	// MCALC   RATE_PITCH 1S IEQN AORATE2 * 3600.0 * 180.0 / 3.14159
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE NPNT PPENG  -10 -4 4 10
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NMAN PPENG  -300 -271 271 300
	// MLIMIT    SET 2 DEFAULT  SWITCHSTATE NSUN PPENG  -400 -360 360 400
	// MLIMSW    AOPCADMD
	calcs.RATE_PITCH = function() {
		var msidList = ['AORATE2'];
		var mnffreq = 32;

		var RATE_PITCH = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORATE2');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		RATE_PITCH.transform = function(args, math, scope) {
			return RATE_PITCH(processScope(scope));
		}

		math.import({
			RATE_PITCH: RATE_PITCH
		});

		RATE_PITCH.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RATE_PITCH()', scope);
			}
		}	
	}();


	// MCALC   RATE_YAW 1S IEQN AORATE3 * 3600.0 * 180.0 / 3.14159
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE NPNT PPENG  -10 -4 4 10
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NMAN PPENG  -300 -271 271 300
	// MLIMIT    SET 2 DEFAULT  SWITCHSTATE NSUN PPENG  -400 -360 360 400
	// MLIMSW    AOPCADMD    
	calcs.RATE_YAW = function() {
		var msidList = ['AORATE3'];
		var mnffreq = 32;

		var RATE_YAW = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORATE3');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		RATE_YAW.transform = function(args, math, scope) {
			return RATE_YAW(processScope(scope));
		}

		math.import({
			RATE_YAW: RATE_YAW
		});

		RATE_YAW.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RATE_YAW()', scope);
			}
		}	
	}();

	// MCALC   ERR_ROLL 1S IEQN AOATTER1 * 3600.0 * 180.0 / 3.14159
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE NPNT PPENG  -10 -5 5 10
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NMAN PPENG  -300 -250 250 300
	// MLIMSW    AOPCADMD
	calcs.ERR_ROLL = function() {
		var msidList = ['AOATTER1'];
		var mnffreq = 32;
		
		var ERR_ROLL = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AOATTER1');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		ERR_ROLL.transform = function(args, math, scope) {
			return ERR_ROLL(processScope(scope));
		}

		math.import({
			ERR_ROLL: ERR_ROLL
		});

		ERR_ROLL.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('ERR_ROLL()', scope);
			}
		}

	}();

	// MCALC   ERR_PITCH 1S IEQN AOATTER2 * 3600.0 * 180.0 / 3.14159
	//MLIMIT    SET 0 DEFAULT  SWITCHSTATE NPNT PPENG  -10 -5 5 10
	//MLIMIT    SET 1 DEFAULT  SWITCHSTATE NMAN PPENG  -300 -250 250 300
	//MLIMSW    AOPCADMD
	calcs.ERR_PITCH = function() {
		var msidList = ['AOATTER2'];
		var mnffreq = 32;

		var ERR_PITCH = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AOATTER2');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		ERR_PITCH.transform = function(args, math, scope) {
			return ERR_PITCH(processScope(scope));
		}

		math.import({
			ERR_PITCH: ERR_PITCH
		});

		ERR_PITCH.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('ERR_PITCH()', scope);
			}
		}	
	}();


	// MCALC   ERR_YAW 1S IEQN AOATTER3 * 3600.0 * 180.0 / 3.14159
	// MLIMIT    SET 0 DEFAULT  SWITCHSTATE NPNT PPENG  -10 -5 5 10
	// MLIMIT    SET 1 DEFAULT  SWITCHSTATE NMAN PPENG  -300 -250 250 300
	// MLIMSW    AOPCADMD  
	calcs.ERR_YAW = function() {
		var msidList = ['AOATTER3'];
		var mnffreq = 32;

		var ERR_YAW = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AOATTER3');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		ERR_YAW.transform = function(args, math, scope) {
			return ERR_YAW(processScope(scope));
		}

		math.import({
			ERR_YAW: ERR_YAW
		});

		ERR_YAW.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('ERR_YAW()', scope);
			}
		}	
	}();

	// MCALC   TOTMOM   1S IEQN SQRT(AOSYMOM1*AOSYMOM1 + AOSYMOM2*AOSYMOM2 + AOSYMOM3*AOSYMOM3)
	// MLIMIT  SET 0 DEFAULT PPENG -1 -1 31.9 40.0
	calcs.TOTMOM = function() {
		var msidList = ['AOSYMOM1', 'AOSYMOM2', 'AOSYMOM3'];
		var mnffreq = 32;
		
		var TOTMOM = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('sqrt((AOSYMOM1^2) + (AOSYMOM2^2) + (AOSYMOM3^2))');
			return eqn.compile().eval(scope);
		}   	

		TOTMOM.transform = function(args, math, scope) {
			return TOTMOM(processScope(scope));
		}

		math.import({
			TOTMOM: TOTMOM
		});

		TOTMOM.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('TOTMOM()', scope);
			}
		}	
	}();

	// MCALC	    RW1 1S IEQN AORWSPD1*60/6.28318530718
	calcs.RW1 = function() {
		var msidList = ['AORWSPD1'];
		var mnffreq = 32;

		var RW1 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORWSPD1');
			return math.unit(eqn.compile().eval(scope), 'rad / s').toNumber('cycle / min');
		}

		RW1.transform = function(args, math, scope) {
			return RW1(processScope(scope));
		}

		math.import({
			RW1: RW1
		});

		RW1.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RW1()', scope);
			}
		}
	}();

	// MCALC	    RW2 1S IEQN AORWSPD2*60/6.28318530718
	calcs.RW2 = function() {
		var msidList = ['AORWSPD2'];
		var mnffreq = 32;

		var RW2 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORWSPD2');
			return math.unit(eqn.compile().eval(scope), 'rad / s').toNumber('cycle / min');
		}

		RW2.transform = function(args, math, scope) {
			return RW2(processScope(scope));
		}

		math.import({
			RW2: RW2
		});

		RW2.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RW2()', scope);
			}
		}
	}();

	// MCALC	    RW3 1S IEQN AORWSPD3*60/6.28318530718
	calcs.RW3 = function() {
		var msidList = ['AORWSPD3'];
		var mnffreq = 32;

		var RW3 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORWSPD3');
			return math.unit(eqn.compile().eval(scope), 'rad / s').toNumber('cycle / min');
		}

		RW3.transform = function(args, math, scope) {
			return RW3(processScope(scope));
		}

		math.import({
			RW3: RW3
		});

		RW3.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RW3()', scope);
			}
		}
	}();

	// MCALC	RW4 1S IEQN AORWSPD4*60/6.28318530718
	calcs.RW4 = function() {
		var msidList = ['AORWSPD4'];
		var mnffreq = 32;

		var RW4 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORWSPD4');
			return math.unit(eqn.compile().eval(scope), 'rad / s').toNumber('cycle / min');
		}

		RW4.transform = function(args, math, scope) {
			return RW4(processScope(scope));
		}

		math.import({
			RW4: RW4
		});

		RW4.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RW4()', scope);
			}
		}
	}();

	// MCALC	    RW5 1S IEQN AORWSPD5*60/6.28318530718
	calcs.RW5 = function() {
		var msidList = ['AORWSPD5'];
		var mnffreq = 32;

		var RW5 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORWSPD5');
			return math.unit(eqn.compile().eval(scope), 'rad / s').toNumber('cycle / min');
		}

		RW5.transform = function(args, math, scope) {
			return RW5(processScope(scope));
		}
		math.import({
			RW5: RW5
		});

		RW5.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RW5()', scope);
			}
		}
	}();

	// MCALC	    RW6 1S IEQN AORWSPD6*60/6.28318530718
	calcs.RW6 = function() {
		var msidList = ['AORWSPD6'];
		var mnffreq = 32;

		var RW6 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = math.parse('AORWSPD6');
			return math.unit(eqn.compile().eval(scope), 'rad / s').toNumber('cycle / min');
		}

		RW6.transform = function(args, math, scope) {
			return RW6(processScope(scope));
		}

		math.import({
			RW6: RW6
		});

		RW6.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('RW6()', scope);
			}
		}
	}();

	calcs.P27VRAILV = function() {
		var msidList = ['5EHSE106', '5HSE202', '5HSE202_P00'];
		var mnffreq = 32;

		var P27VRAILV = function(scope) {
			if (nullCheck(scope) === true) {
				return null;
			}

			var eqn = math.parse('( (((MSID_5EHSE106 % 2) == 0) * MSID_5HSE202) + (((MSID_5EHSE106 % 2) == 1) * MSID_5HSE202_P00) )');
			var result = eqn.compile().eval(scope);
	
			// if (result !== 26.962) {
			//	console.log(scope);
			// }

			return eqn.compile().eval(scope);
		}

		// FIXME - Need to do the MSID_ thing because all start with a number
		// Figure out if semicolon will work.

		// FIXME: This does not use the processScope function
		// because of the need for previous values. Figure out later.
		P27VRAILV.transform = function(args, math, scope) {
			var finalModel = {};
			
			//var re = "/(\S+)\_P(\d+)/i";
			var re = /(\S+)_P(\d+)/;

			_.each(scope, function(m) {
				var name = m.get('name');
				
				var match = name.match(re);

				var msid = name;
				var prevNum = -1;

				if (match !== null) {    	   			
					msid = match[1];
					prevNum = Number(match[2]);
				}

				var raw_val;
				var final_val = null;

				var modelOfInterest = null
				for (var i=0; i < scope.length; i++) {
					if (scope[i].get('name') === msid) {
						modelOfInterest = scope[i];
						break;
					}
				}
				
				if (prevNum === -1) {
					raw_val = modelOfInterest.get('value');
				} else {     				
					var prevValues = modelOfInterest.get('prevvalues');

					if (prevValues.length > prevNum) {
						raw_val = prevValues[prevNum];
					} else {
						raw_val = null;
					}
				}

				var final_val = null;

				if (raw_val !== null) {
					final_val = Number(raw_val);
				}

				var key = "MSID_" + name;

				finalModel[key] = final_val;
			});	

			return P27VRAILV(finalModel);

		}

		math.import({
			P27VRAILV: P27VRAILV
		});

		P27VRAILV.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('P27VRAILV()', scope);
			}
		}
	}();

	// Returns HH:MM
	calcs.A_FREEMEM = function() {
		var msidList = ['COSARCPT', 'COSAPBPT'];
		var mnffreq = 128;
		
		var A_FREEMEM = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = 
				math.parse('(134217728-((COSARCPT-COSAPBPT+134217728) % 134217728)) / (32000 / 16)',
						scope);
			var mem = eqn.compile().eval(scope);

			var mem_min = Math.floor(mem / 60);
			var mem_sec = mem - (mem_min * 60);

			var mem_hour = Math.floor(mem / 3600);
			var mem_min = Math.floor((mem % 3600) / 60);
			return mem_hour + ":" + ((mem_min < 10) ? "0" + mem_min : mem_min);
		}

		A_FREEMEM.transform = function(args, math, scope) {			
			return A_FREEMEM(processScope(scope));
		}

		math.import({
			A_FREEMEM: A_FREEMEM
		});

		A_FREEMEM.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('A_FREEMEM()', scope);
			}
		}
	}();

	// Returns HH:MM
	calcs.B_FREEMEM = function() {
		var msidList = ['COSBRCPT', 'COSBPBPT'];
		var mnffreq = 128;
		
		var B_FREEMEM = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var eqn = 
				math.parse('(134217728-((COSBRCPT-COSBPBPT+134217728) % 134217728)) / (32000 / 16)',
						scope);
			var mem = eqn.compile().eval(scope);
			var mem_hour = Math.floor(mem / 3600);
			var mem_min = Math.floor((mem % 3600) / 60);

			return mem_hour + ":" + ((mem_min < 10) ? "0" + mem_min : mem_min);
		}

		B_FREEMEM.transform = function(args, math, scope) {
			return B_FREEMEM(processScope(scope));
		}


		math.import({
			B_FREEMEM: B_FREEMEM
		});

		B_FREEMEM.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('B_FREEMEM()', scope);
			}
		}
	}();

	// Returns HH:MM
	calcs.A_TIMETODUMP = function() {
		var msidList = ['CIUMBITR', 
		                'CVCMNCTR', 
		                'COSARCPT', 
		                'COSAPBPT',
		                'COSAPBEN',
		                'CSSR1CVA'];

		var mnffreq = 128;
		
		var A_TIMETODUMP = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var pb_ptr_eqn = math.parse('((CVCMNCTR - 66 + 128) % 128) * (((CIUMBITR - 32000) / 16) * 0.25625)',
					scope);
			scope['PB_PTR'] = pb_ptr_eqn.compile().eval(scope);

			var rc_ptr_eqn = math.parse('((CVCMNCTR - 34 +128) % 128) * 512.5', scope);
			scope['RC_PTR'] = rc_ptr_eqn.compile().eval(scope);


			var dump_ssra_eqn = math.parse('(((COSARCPT + (RC_PTR * (CSSR1CVA==1)) - COSAPBPT - (PB_PTR * (COSAPBEN==1)) + 134217728) % 134217728) / ((CIUMBITR-64000) / 16))',
					scope);
			var ttd_ssra = dump_ssra_eqn.compile().eval(scope);

			var ttd_ssra_min = Math.floor(ttd_ssra / 60);
			var ttd_ssra_sec = Math.floor(ttd_ssra - (ttd_ssra_min*60));
			return ttd_ssra_min + ":" + ((ttd_ssra_sec < 10) ? "0" + ttd_ssra_sec : ttd_ssra_sec);
		}

		A_TIMETODUMP.transform = function(args, math, scope) {
			var finalModel = processScope(scope);
			
			var result = $.grep(scope, function(e) { return e.get('name') === "CIUMBITR"; });
			
			if (result[0].get('value') !== null) {
				finalModel['CIUMBITR'] = convertBitrate(result[0].get('value'));
			}
			
			return A_TIMETODUMP(finalModel);
		}

		math.import({
			A_TIMETODUMP: A_TIMETODUMP
		});

		A_TIMETODUMP.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('A_TIMETODUMP()', scope);
			}
		}
	}();

	calcs.B_TIMETODUMP = function() {
		var msidList = ['CIUMBITR', 
		                'CVCMNCTR', 
		                'COSBRCPT', 
		                'COSBPBPT',
		                'COSBPBEN',
		                'CSSR2CVA'];

		var mnffreq = 128;
		
		var B_TIMETODUMP = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var pb_ptr_eqn = math.parse('((CVCMNCTR - 66 + 128) % 128) * (((CIUMBITR - 32000) / 16) * 0.25625)',
					scope);

			scope['PB_PTR'] = pb_ptr_eqn.compile().eval(scope);


			var rc_ptr_eqn = math.parse('((CVCMNCTR - 34 +128) % 128) * 512.5', scope);
			scope['RC_PTR'] = rc_ptr_eqn.compile().eval(scope);

			var dump_ssrb_eqn = math.parse('(((COSBRCPT + (RC_PTR * (CSSR2CVA==1)) - COSBPBPT - (PB_PTR * (COSBPBEN==1)) + 134217728) % 134217728) / ((CIUMBITR-64000) / 16))',
					scope);

			var ttd_ssrb = dump_ssrb_eqn.compile().eval(scope);

			var ttd_ssrb_min = Math.floor(ttd_ssrb / 60);
			var ttd_ssrb_sec = Math.floor(ttd_ssrb - (ttd_ssrb_min*60));
			return ttd_ssrb_min + ":" + ((ttd_ssrb_sec < 10) ? "0" + ttd_ssrb_sec : ttd_ssrb_sec);
		}

		B_TIMETODUMP.transform = function(args, math, scope) {
			var finalModel = processScope(scope);
			
			var result = $.grep(scope, function(e) { return e.get('name') === "CIUMBITR"; });
			
			if (result[0].get('value') !== null) {
				finalModel['CIUMBITR'] = convertBitrate(result[0].get('value'));
			}

			return B_TIMETODUMP(finalModel);
		}

		math.import({
			B_TIMETODUMP: B_TIMETODUMP
		});

		B_TIMETODUMP.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('B_TIMETODUMP()', scope);
			}
		}
	}();

	calcs.A_ROLLTIME = function() {
		var msidList = ['COSARCPT', 'COSAPBPT'];
		var mnffreq = 128;
		
		var A_ROLLTIME = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var a_mem_sec_eqn = 
				math.parse('(134217728-((COSARCPT-COSAPBPT+134217728) % 134217728)) / (32000 / 16)',
						scope);
			var a_mem_sec = a_mem_sec_eqn.compile().eval(scope);

			var roll_date = new Date();
			roll_date.setSeconds(roll_date.getSeconds() + a_mem_sec);

			var roll_year = roll_date.getUTCFullYear();

			var roll_year_onejan = Date.UTC(roll_year, 0, 1);

			var roll_doy = Math.ceil( (roll_date - roll_year_onejan) / 86400000);
			if (roll_doy < 100) {
				roll_doy = "0" + roll_doy;
			}
			if (roll_doy < 10) {
				roll_doy = "0" + roll_doy;
			}

			var roll_hour = roll_date.getUTCHours();
			if (roll_hour < 10) {
				roll_hour = "0" + roll_hour;
			}

			var roll_min = roll_date.getUTCMinutes();
			if (roll_min < 10) {
				roll_min = "0" + roll_min;
			}

			return roll_year + ":" + roll_doy + ":" + roll_hour + ":" + roll_min;
		}

		A_ROLLTIME.transform = function(args, math, scope) {
			return A_ROLLTIME(processScope(scope));
		}


		math.import({
			A_ROLLTIME: A_ROLLTIME
		});

		A_ROLLTIME.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('A_ROLLTIME()', scope);
			}
		}
	}();

	calcs.B_ROLLTIME = function() {
		var msidList = ['COSBRCPT', 'COSBPBPT'];
		var mnffreq = 128;

		var B_ROLLTIME = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var b_mem_sec_eqn = 
				math.parse('(134217728-((COSBRCPT-COSBPBPT+134217728) % 134217728)) / (32000 / 16)',
						scope);
			var b_mem_sec = b_mem_sec_eqn.compile().eval(scope);

			var roll_date = new Date();
			roll_date.setSeconds(roll_date.getSeconds() + b_mem_sec);

			var roll_year = roll_date.getUTCFullYear();

			var roll_year_onejan = Date.UTC(roll_year, 0, 1);

			var roll_doy = Math.ceil( (roll_date - roll_year_onejan) / 86400000);
			if (roll_doy < 100) {
				roll_doy = "0" + roll_doy;
			}
			if (roll_doy < 10) {
				roll_doy = "0" + roll_doy;
			}

			var roll_hour = roll_date.getUTCHours();
			if (roll_hour < 10) {
				roll_hour = "0" + roll_hour;
			}

			var roll_min = roll_date.getUTCMinutes();
			if (roll_min < 10) {
				roll_min = "0" + roll_min;
			}

			return roll_year + ":" + roll_doy + ":" + roll_hour + ":" + roll_min;
		}

		B_ROLLTIME.transform = function(args, math, scope) {
			return B_ROLLTIME(processScope(scope));
		}


		math.import({
			B_ROLLTIME: B_ROLLTIME
		});

		B_ROLLTIME.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('B_ROLLTIME()', scope);
			}
		}
	}();

	calcs.A_PBCMPT = function() {
		var msidList = ['CIUMBITR', 
		                'CVCMNCTR', 
		                'COSARCPT', 
		                'COSAPBPT',
		                'COSAPBEN',
		                'CSSR1CVA'];
		var mnffreq = 128;
		
		var A_PBCMPT = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var pb_ptr_eqn = math.parse('((CVCMNCTR - 66 + 128) % 128) * (((CIUMBITR - 32000) / 16) * 0.25625)',
					scope);

			scope['PB_PTR'] = pb_ptr_eqn.compile().eval(scope);


			var rc_ptr_eqn = math.parse('((CVCMNCTR - 34 +128) % 128) * 512.5', scope);
			scope['RC_PTR'] = rc_ptr_eqn.compile().eval(scope);

			var dump_ssra_eqn = math.parse('(((COSARCPT + (RC_PTR * (CSSR1CVA==1)) - COSAPBPT - (PB_PTR * (COSAPBEN==1)) + 134217728) % 134217728) / ((CIUMBITR-64000) / 16))',
					scope);

			var ttd_ssra = dump_ssra_eqn.compile().eval(scope);

			var done_date = new Date();
			done_date.setSeconds(done_date.getSeconds() + ttd_ssra);

			var done_year = done_date.getUTCFullYear();

			var done_year_onejan = Date.UTC(done_year, 0, 1);

			var done_doy = Math.ceil( (done_date - done_year_onejan) / 86400000);
			if (done_doy < 100) {
				done_doy = "0" + done_doy;
			}
			if (done_doy < 10) {
				done_doy = "0" + done_doy;
			}

			var done_hour = done_date.getUTCHours();
			if (done_hour < 10) {
				done_hour = "0" + done_hour;
			}

			var done_min = done_date.getUTCMinutes();
			if (done_min < 10) {
				done_min = "0" + done_min;
			}

			return done_year + ":" + done_doy + ":" + done_hour + ":" + done_min;
		}

		A_PBCMPT.transform = function(args, math, scope) {
			var finalModel = processScope(scope);
			
			var result = $.grep(scope, function(e) { return e.get('name') === "CIUMBITR"; });
			
			if (result[0].get('value') !== null) {
				finalModel['CIUMBITR'] = convertBitrate(result[0].get('value'));
			}
			
			return A_PBCMPT(finalModel);
		}

		math.import({
			A_PBCMPT: A_PBCMPT
		});

		A_PBCMPT.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('A_PBCMPT()', scope);
			}
		}
	}();

	calcs.B_PBCMPT = function() {
		var msidList = ['CIUMBITR', 
		                'CVCMNCTR', 
		                'COSBRCPT', 
		                'COSBPBPT',
		                'COSBPBEN',
		                'CSSR2CVA'];
		var mnffreq = 128;

		var B_PBCMPT = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}

			var pb_ptr_eqn = math.parse('((CVCMNCTR - 66 + 128) % 128) * (((CIUMBITR - 32000) / 16) * 0.25625)',
					scope);

			scope['PB_PTR'] = pb_ptr_eqn.compile().eval(scope);


			var rc_ptr_eqn = math.parse('((CVCMNCTR - 34 +128) % 128) * 512.5', scope);
			scope['RC_PTR'] = rc_ptr_eqn.compile().eval(scope);

			var dump_ssra_eqn = math.parse('(((COSBRCPT + (RC_PTR * (CSSR2CVA==1)) - COSBPBPT - (PB_PTR * (COSBPBEN==1)) + 134217728) % 134217728) / ((CIUMBITR-64000) / 16))',
					scope);

			var ttd_ssra = dump_ssra_eqn.compile().eval(scope);

			var done_date = new Date();
			done_date.setSeconds(done_date.getSeconds() + ttd_ssra);

			var done_year = done_date.getUTCFullYear();

			var done_year_onejan = Date.UTC(done_year, 0, 1);

			var done_doy = Math.ceil( (done_date - done_year_onejan) / 86400000);
			if (done_doy < 100) {
				done_doy = "0" + done_doy;
			}
			if (done_doy < 10) {
				done_doy = "0" + done_doy;
			}

			var done_hour = done_date.getUTCHours();
			if (done_hour < 10) {
				done_hour = "0" + done_hour;
			}

			var done_min = done_date.getUTCMinutes();
			if (done_min < 10) {
				done_min = "0" + done_min;
			}

			return done_year + ":" + done_doy + ":" + done_hour + ":" + done_min;
		}

		B_PBCMPT.transform = function(args, math, scope) {
			var finalModel = processScope(scope);
			
			var result = $.grep(scope, function(e) { return e.get('name') === "CIUMBITR"; });
			
			if (result[0].get('value') !== null) {
				finalModel['CIUMBITR'] = convertBitrate(result[0].get('value'));
			}
			return B_PBCMPT(finalModel);
		}

		math.import({
			B_PBCMPT: B_PBCMPT
		});

		B_PBCMPT.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('B_PBCMPT()', scope);
			}
		}
	}();

	calcs.SNAP_RA = function() {
		var msidList = ['AOATTQT1', 'AOATTQT2', 'AOATTQT3', 'AOATTQT4'];
		var mnffreq = 128;

		var SNAP_RA = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('atan2( (2*((AOATTQT1*AOATTQT2)+(AOATTQT3*AOATTQT4))), (AOATTQT1^2 - AOATTQT2^2 - AOATTQT3^2 + AOATTQT4^2) )');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}   	

		SNAP_RA.transform = function(args, math, scope) {
			return SNAP_RA(processScope(scope));
		}

		math.import({
			SNAP_RA: SNAP_RA
		});

		SNAP_RA.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_RA()', scope);
			}
		}	
	}();

	calcs.SNAP_DEC = function() {
		var msidList = ['AOATTQT1', 'AOATTQT2', 'AOATTQT3', 'AOATTQT4'];
		var mnffreq = 128;
				
		var SNAP_DEC = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var x_n_eqn = math.parse('2 * ((AOATTQT1*AOATTQT3) - (AOATTQT2*AOATTQT4))');
			scope['X_N'] = x_n_eqn.compile().eval(scope);
			
			var eqn = math.parse('atan2(X_N, sqrt(1-(X_N ^ 2)))');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}   	

		SNAP_DEC.transform = function(args, math, scope) {			
			return SNAP_DEC(processScope(scope));
		}

		math.import({
			SNAP_DEC: SNAP_DEC
		});

		SNAP_DEC.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_DEC()', scope);
			}
		}	
	}();
	
	calcs.SNAP_ROLL = function() {
		var msidList = ['AOATTQT1', 'AOATTQT2', 'AOATTQT3', 'AOATTQT4'];
		var mnffreq = 128;
		
		var SNAP_ROLL = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var y_n_eqn = math.parse('2 * ((AOATTQT2*AOATTQT3) + (AOATTQT1*AOATTQT4))');
			scope['Y_N'] = y_n_eqn.compile().eval(scope);
			
			var z_n_eqn = math.parse('(AOATTQT3^2) + (AOATTQT4^2) - (AOATTQT1^2) - (AOATTQT2^2)');
			scope['Z_N'] = z_n_eqn.compile().eval(scope);
			
			var eqn = math.parse('atan2(Y_N, Z_N)');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('deg');
		}   	

		SNAP_ROLL.transform = function(args, math, scope) {			
			return SNAP_ROLL(processScope(scope));
		}

		math.import({
			SNAP_ROLL: SNAP_ROLL
		});

		SNAP_ROLL.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_ROLL()', scope);
			}
		}	
	}();

	calcs.ACAOBJ = function() {
		var msidList = ['AOACFID0', 
		                'AOACFID1', 
		                'AOACFID2', 
		                'AOACFID3', 
		                'AOACFID4', 
		                'AOACFID5',
		                'AOACFID6',
		                'AOACFID7']
		
		var mnffreq = 128;
				
		var ACAOBJ = function(scope) {			
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var result = "";
			
			for (var i=0; i < msidList.length; i++) {
				result += scope[msidList[i]];
			}
			
			return result;
		}   	

		ACAOBJ.transform = function(args, math, scope) {
			// Do this manually- processScope deals with numeric values
			
			var finalModel = {};
				
			_.each(scope, function(m) {
				
				var name = m.get('name');
				var raw_val = m.get('value');
				
				var final_val = null;

				if (raw_val !== null) {
					final_val = raw_val.substring(0, 1);
				}

				finalModel[name] = final_val;
			});

			return ACAOBJ(finalModel);
		}

		math.import({
			ACAOBJ: ACAOBJ
		});

		ACAOBJ.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('ACAOBJ()', scope);
			}
		}	
	}();
	
	calcs.ACAFCT = function() {
		var msidList = ['AOACFCT0', 
		                'AOACFCT1', 
		                'AOACFCT2', 
		                'AOACFCT3', 
		                'AOACFCT4', 
		                'AOACFCT5',
		                'AOACFCT6',
		                'AOACFCT7']
		
		var mnffreq = 128;
				
		var ACAFCT = function(scope) {			
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var result = "";
			
			for (var i=0; i < msidList.length; i++) {
				result += scope[msidList[i]];
			}
			
			return result;
		}   	

		ACAFCT.transform = function(args, math, scope) {			
			var finalModel = {};
			
			_.each(scope, function(m) {
				
				var name = m.get('name');
				var raw_val = m.get('value');
				
				var final_val = null;

				if (raw_val !== null) {
					final_val = raw_val.substring(0, 1);
				}

				finalModel[name] = final_val;
			});

			return ACAFCT(finalModel);
		}

		math.import({
			ACAFCT: ACAFCT
		});

		ACAFCT.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('ACAFCT()', scope);
			}
		}	
	}();
	
	calcs.SOCB1 = function() {
		var msidList = ['EOCHRGB1'];
		var mnffreq = 128;
		
		var SOCB1 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn;
			
			if (scope['EOCHRGB1'] > 120) {
				eqn = math.parse('EOCHRGB1 / 100');
			} else {
				eqn = math.parse('EOCHRGB1 * 100');
			}
			
			return eqn.compile().eval(scope);
		}   	

		SOCB1.transform = function(args, math, scope) {			
			return SOCB1(processScope(scope));
		}

		math.import({
			SOCB1: SOCB1
		});

		SOCB1.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SOCB1()', scope);
			}
		}	
	}();	
	
	calcs.SOCB2 = function() {
		var msidList = ['EOCHRGB1'];
		var mnffreq = 128;
		
		var SOCB2 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}			
			var eqn;
			
			if (scope['EOCHRGB1'] > 120) {
				eqn = math.parse('EOCHRGB1 / 100');
			} else {
				eqn = math.parse('EOCHRGB1 * 100');
			}
			
			return eqn.compile().eval(scope);
		}   	

		SOCB2.transform = function(args, math, scope) {
			return SOCB2(processScope(scope));
		}

		math.import({
			SOCB2: SOCB2
		});

		SOCB2.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SOCB2()', scope);
			}
		}	
	}();
	
	calcs.SOCB3 = function() {
		var msidList = ['EOCHRGB1'];
		var mnffreq = 128;
		
		var SOCB3 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn;
			
			if (scope['EOCHRGB1'] > 120) {
				eqn = math.parse('EOCHRGB1 / 100');
			} else {
				eqn = math.parse('EOCHRGB1 * 100');
			}
			
			return eqn.compile().eval(scope);
		}   	

		SOCB3.transform = function(args, math, scope) {
			return SOCB3(processScope(scope));
		}

		math.import({
			SOCB3: SOCB3
		});

		SOCB3.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SOCB3()', scope);
			}
		}	
	}();

	calcs.ACISTAT = function() {
		var msidList = ['1STAT7ST', 
		                '1STAT6ST', 
		                '1STAT5ST',
		                '1STAT4ST',
		                '1STAT3ST',
		                '1STAT2ST',
		                '1STAT1ST',
		                '1STAT0ST'];
		var mnffreq = 128;
		
		var ACISTAT = function(scope) {			
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('(MSID_1STAT7ST << 7) + \
								  (MSID_1STAT6ST << 6) + \
								  (MSID_1STAT5ST << 5) + \
								  (MSID_1STAT4ST << 4) + \
				   	    		  (MSID_1STAT3ST << 3) + \
					              (MSID_1STAT2ST << 2) + \
								  (MSID_1STAT1ST << 1) + \
					    		  (MSID_1STAT0ST)');
			
			return eqn.compile().eval(scope);
		}   	

		ACISTAT.transform = function(args, math, scope) {
			return ACISTAT(processScope(scope));
		}

		math.import({
			ACISTAT: ACISTAT
		});

		ACISTAT.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('ACISTAT()', scope);
			}
		}	
	}();
	
	calcs.SNAP_DITHYANG = function() {
		var msidList = ['AODITHR3'];
		var mnffreq = 128;

		var SNAP_DITHYANG = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AODITHR3');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		SNAP_DITHYANG.transform = function(args, math, scope) {
			return SNAP_DITHYANG(processScope(scope));
		}

		math.import({
			SNAP_DITHYANG: SNAP_DITHYANG
		});

		SNAP_DITHYANG.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_DITHYANG()', scope);
			}
		}
	}();
	
	calcs.SNAP_DITHZANG = function() {
		var msidList = ['AODITHR2'];
		var mnffreq = 128;

		var SNAP_DITHZANG = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AODITHR2');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		SNAP_DITHZANG.transform = function(args, math, scope) {
			return SNAP_DITHZANG(processScope(scope));
		}

		math.import({
			SNAP_DITHZANG: SNAP_DITHZANG
		});

		SNAP_DITHZANG.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_DITHZANG()', scope);
			}
		}
	}();
	
	calcs.SNAP_AACCCDPT = function() {
		var msidList = ['AACCCDPT'];
		var mnffreq = 128;

		var SNAP_AACCCDPT = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AACCCDPT');
			return math.unit(eqn.compile().eval(scope), 'degF').toNumber('degC');
		}

		SNAP_AACCCDPT.transform = function(args, math, scope) {
			return SNAP_AACCCDPT(processScope(scope));
		}

		math.import({
			SNAP_AACCCDPT: SNAP_AACCCDPT
		});

		SNAP_AACCCDPT.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_AACCCDPT()', scope);
			}
		}
	}();
	
	calcs.SNAP_AOACINTT = function() {
		var msidList = ['AOACINTT'];
		var mnffreq = 128;
		

		var SNAP_AOACINTT = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AOACINTT / 1000');
			return eqn.compile().eval(scope);
		}

		SNAP_AOACINTT.transform = function(args, math, scope) {
			return SNAP_AOACINTT(processScope(scope));
		}

		math.import({
			SNAP_AOACINTT: SNAP_AOACINTT
		});

		SNAP_AOACINTT.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_AOACINTT()', scope);
			}
		}
	}();
	
	calcs.SNAP_AOGBIAS1 = function() {
		var msidList = ['AOGBIAS1'];
		var mnffreq = 128;

		var SNAP_AOGBIAS1 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AOGBIAS1');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		SNAP_AOGBIAS1.transform = function(args, math, scope) {
			return SNAP_AOGBIAS1(processScope(scope));
		}

		math.import({
			SNAP_AOGBIAS1: SNAP_AOGBIAS1
		});

		SNAP_AOGBIAS1.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_AOGBIAS1()', scope);
			}
		}
	}();
	
	calcs.SNAP_AOGBIAS2 = function() {
		var msidList = ['AOGBIAS2'];
		var mnffreq = 128;

		var SNAP_AOGBIAS2 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AOGBIAS2');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		SNAP_AOGBIAS2.transform = function(args, math, scope) {
			return SNAP_AOGBIAS2(processScope(scope));
		}

		math.import({
			SNAP_AOGBIAS2: SNAP_AOGBIAS2
		});

		SNAP_AOGBIAS2.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_AOGBIAS2()', scope);
			}
		}
	}();
	
	calcs.SNAP_AOGBIAS3 = function() {
		var msidList = ['AOGBIAS3'];
		var mnffreq = 128;

		var SNAP_AOGBIAS3 = function(scope) {
			if (nullCheck(scope) == true) {
				return null;
			}
			
			var eqn = math.parse('AOGBIAS3');
			return math.unit(eqn.compile().eval(scope), 'rad').toNumber('arcsec');
		}

		SNAP_AOGBIAS3.transform = function(args, math, scope) {
			return SNAP_AOGBIAS3(processScope(scope));
		}

		math.import({
			SNAP_AOGBIAS3: SNAP_AOGBIAS3
		});

		SNAP_AOGBIAS3.transform.rawArgs = true;

		return {
			getMSIDList: function() {
				return msidList;
			},

			getMNFFreq: function() {
				return mnffreq;
			},

			run: function(scope) {
				return math.eval('SNAP_AOGBIAS3()', scope);
			}
		}
	}();
	
	return calcs;
};
