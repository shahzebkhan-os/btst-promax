from src.options.iv_surface import fit_iv_surface

def test_iv_surface():
    f = fit_iv_surface([100,110,120],[0.2,0.22,0.25])
    assert callable(f)
