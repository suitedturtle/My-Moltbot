for e,a in zip(expected, actual)]
            print(f"\n📊 Errors: {errors}")
            print(f"📈 Max error: {max(errors):.