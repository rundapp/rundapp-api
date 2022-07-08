from datetime import date
from typing import Any, Mapping, Optional

from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.schemas.strava import RefreshTokenResponse, TokenExchangeResponse
from tests.constants import (
    CHALLENGE_FAILING_DISTANCE,
    CHALLENGE_PASSING_ACTIVITY_ID,
    CHALLENGE_PASSING_DISTANCE,
)


class MockStravaClient(IStravaClient):
    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Makes API call."""

    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refreshes a Strava athlete's access token."""

        response = {
            "token_type": "Bearer",
            "access_token": "fc1e6a50b103f8d5402850eaa67e3ae0f12ffd66",
            "expires_at": 1655427443,
            "expires_in": 19293,
            "refresh_token": "e1adf2fb22c578b9336465a38ecaa5b439f06b57",
        }

        return RefreshTokenResponse(**response)

    async def exhange_code_for_token(self, code: str) -> TokenExchangeResponse:
        """Exchanges code recieved from Strava for athlete's access token."""

        response = {
            "token_type": "Bearer",
            "expires_at": 1655511405,
            "expires_in": 21600,
            "refresh_token": "b292bcbc4c11e13f451d81b56aacd9fc7c244395",
            "access_token": "d9d14255fa18a289610f34c33a703ec77a0ffd26",
            "athlete": {
                "id": 104459479,
            },
        }

        return TokenExchangeResponse(**response)

    async def get_activity(
        self, access_token: str, activity_id: int
    ) -> Mapping[str, Any]:
        """Retrieves a Strava athlete's activity. Returns a massive JSON response."""

        distance = (
            CHALLENGE_PASSING_DISTANCE
            if activity_id == CHALLENGE_PASSING_ACTIVITY_ID
            else CHALLENGE_FAILING_DISTANCE
        )

        year = date.today().year + 1

        return {
            "distance": distance,
            "type": "Run",
            "start_date": f"{year}-07-06T03:33:56Z",
            "map": {
                "id": "a7316374637",
                "polyline": "wuk}Ftz~tOED@FAI@@BGIICYQWOIMOCO@QAa@DOBc@DCTq@DEh@oALQXu@LOTu@r@{AJG\\GHGBO@k@CsAAUIQSIsC?SAu@Oo@@QAUKw@y@_Ay@]IU?WB[LUNKNqAbDU\\W~@KPQx@{@zCo@~BG^Af@@nBQ`ASz@IxAENS`@WtAOfBEnA?l@GTg@r@g@hA]l@sBxEQx@{@bBQr@mCdGW`@Yr@Wr@c@|A{@lBEP]x@s@lAa@jAWd@cCpFc@z@Yb@a@jAw@fBQVy@XQTGXO^WbAa@dAMj@OV_@`@U\\_@p@KXI^C~@ERsChGiAxBUvAq@vA]n@OHSn@OP_A`BW\\QHETMPOJMXYRSVa@x@MJi@Ts@t@]VeDxDOVQj@Kv@?d@Fn@Lb@lAnCr@fBnArCtAhDn@xAHNFDFLVPRHn@FT?VIb@U^i@L_@Hc@@[?k@Dm@Ei@Ig@MWYe@CK?ONM^e@LIj@q@f@e@vA_BLEXDhAGnBc@`A]t@Ql@E~@?bAJn@XR?v@Ir@H`@JnAn@j@^h@TJHlB|@|ChBPL\\b@Th@\\p@vAfBR^FD|@xAf@p@dAlAx@dAN@LCFGZg@HGDMxAoBVUVBd@d@^Vf@N^Bn@GRITO~@y@l@w@PYBAJWb@w@PUPMRGN?bEN`@I\\YR_@Lk@DoAAM@m@?mAFYLWj@?d@INAbC?DAn@BrACl@@h@?JCDIBo@F_@B_@?{BBa@Cq@?m@Em@B_AJYRYHSNG^Ib@YR?PHN?PG`Ag@VSXIr@GPIn@MlAKLEPSJYP_A@_@Eq@DGNG@GIOKGCI@YEwBAoEC_A?{BCsBDiACy@@y@AaA@OLa@?IMe@OeAYuCEyA@gBCaBCg@BWBECm@Ba@Cy@@iCIiBBiAAk@?sAAOD?Gc@?e@EwA@u@@GEmAHqAEiADiAAiB@UAQ?a@SuB?SCk@BIAQBs@Dc@EcCBWC_AEa@Ga@YiAAYU]g@WWYISKu@KMMKYO}@Yy@K_@FiADsAIeAMK?IBIEe@CkB@IAO@[@gACgABuAAECEMYeBIGSA[Ba@TOLOF}AV_@PGFAz@HTVVFPDRATQj@mAxB",
                "resource_state": 3,
                "summary_polyline": "wuk}Ftz~tOED@FAI@@BGIICYQWOIMOCO@QAa@DOBc@DCTq@DEh@oALQXu@LOTu@r@{AJG\\GHGBO@k@CyAAOIQSIsC?SAu@Oo@@YEMGw@y@_Ay@]IU?WB[LUNKNqAbDONO`@Mj@KPQx@{@zCq@fCEVAf@@nBQ`ASz@IxAENS`@WtAOfBEnA?l@GTg@r@g@hA]l@sBxEQx@{@bBQr@mCdGW`@Yr@Wr@c@|A{@lBEP]x@s@lAa@jAWd@cCpFc@z@Yb@a@jAw@fBQVy@XQTGXO^WbAa@dAMj@OV_@`@U\\_@p@KXI^C~@ERsChGiAxBUvAq@vA]n@OHSn@OP_A`BW\\QHETMPOJMXYRSVa@x@MJi@Ts@t@]VeDxDOVQj@Kv@?d@Fn@Lb@lAnCr@fBnArCtAhDn@xAHNFDFLVPRHn@FT?VI`@U`@i@L_@Hc@@[?k@Dm@Ei@Ig@MWYe@CK?ONM^e@LIj@q@f@e@vA_BLEXDhAGnBc@`A]t@Ql@E~@?bAJn@XR?v@Ir@H`@JnAn@j@^h@TJHlB|@|ChBPL\\b@Th@\\p@vAfBR^FD|@xAf@p@dAlAx@dAL@NCdBeCp@{@LIVBd@d@^Vf@N^Bn@GRITO~@y@l@w@PYBAJWb@w@PUPMRGN?vDNRAXG\\YPYNq@DoAAM@m@?mAFYLWj@?d@INAbC?DAn@BrACl@@h@?JCDIBo@F_@B_@?{BBa@Cq@?m@Em@B_AJYRYHSNG^Ib@YR?PHN?PG`Ag@VSXIr@GPIn@MlAKLEPSJYP_A@_@Eq@DGNG@GIOKGCI@YEwBAoEC_A?{BCsBDiACy@@y@AaA@OLa@?IMe@OeAYuCEyA@gBCaBCg@BWBECm@Ba@Cy@@iCIiBBiAAk@?sAAOD?Gc@?e@EwA@u@@GEmAHqAEiADiAAiB@UAQ?a@SuB?SCk@BIAQBs@Dc@EcCBWC_AEa@Ga@YiAAYU]g@WWYISKu@KMMKYO}@Yy@K_@FiADsAIeAMK?IBIEe@CkB@IAO@[@gACgABuAAECEMYeBIGSA[Ba@TOLOF}AV_@PGFAz@HTVVFPDRATQj@mAxB",
            },
            "manual": False,
            "average_speed": 2.997,
        }
