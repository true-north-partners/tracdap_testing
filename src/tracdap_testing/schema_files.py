
import tracdap.rt.api as trac

import src.tracdap_testing.schemas as schemas
import src.tracdap_testing.using_data as using_data


class SchemaFilesModel(trac.TracModel):

    def define_attributes(self) -> list[trac.TagUpdate]:

        return trac.define_attributes(
            trac.A("model_description", "A example model, for testing purposes"),
            trac.A("business_segment", "retail_products", categorical=True),
            trac.A("classifiers", ["loans", "uk", "examples"], attr_type=trac.STRING)
        )

    def define_parameters(self) -> dict[str, trac.ModelParameter]:

        return trac.define_parameters(

            trac.P("eur_usd_rate", trac.FLOAT,
                   label="EUR/USD spot rate for reporting"),

            trac.P("default_weighting", trac.FLOAT,
                   label="Weighting factor applied to the profit/loss of a defaulted loan"),

            trac.P("filter_defaults", trac.BOOLEAN,
                   label="Exclude defaulted loans from the calculation",
                   default_value=False))

    def define_inputs(self) -> dict[str, trac.ModelInputSchema]:

        customer_loans = trac.load_schema(schemas, "customer_loans.csv")

        return {"customer_loans": trac.ModelInputSchema(customer_loans)}

    def define_outputs(self) -> dict[str, trac.ModelOutputSchema]:

        profit_by_region = trac.load_schema(schemas, "profit_by_region.csv")

        return {"profit_by_region": trac.ModelOutputSchema(profit_by_region)}

    def run_model(self, ctx: trac.TracContext):

        eur_usd_rate = ctx.get_parameter("eur_usd_rate")
        default_weighting = ctx.get_parameter("default_weighting")
        filter_defaults = ctx.get_parameter("filter_defaults")

        customer_loans = ctx.get_pandas_table("customer_loans")

        profit_by_region = using_data.calculate_profit_by_region(
            customer_loans, eur_usd_rate,
            default_weighting, filter_defaults)

        ctx.put_pandas_table("profit_by_region", profit_by_region)


if __name__ == "__main__":
    import tracdap.rt.launch as launch
    launch.launch_model(SchemaFilesModel, "config/using_data.yaml", "config/sys_config.yaml")