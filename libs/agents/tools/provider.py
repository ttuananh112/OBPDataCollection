def create_blueprint(rolename='scenario', color=None, actor_category="car", safe=False):
    """
    Function to setup the blueprint of an actor given its model and other relevant parameters
    """

    _actor_blueprint_categories = {
        'car': 'vehicle.tesla.model3',
        'van': 'vehicle.volkswagen.t2',
        'truck': 'vehicle.carlamotors.carlacola',
        'trailer': '',
        'semitrailer': '',
        'bus': 'vehicle.volkswagen.t2',
        'motorbike': 'vehicle.kawasaki.ninja',
        'bicycle': 'vehicle.diamondback.century',
        'train': '',
        'tram': '',
        'pedestrian': 'walker.pedestrian.0001',
    }

    # The model is not part of the blueprint library. Let's take a default one for the given category
    bp_filter = "vehicle.*"
    new_model = _actor_blueprint_categories[actor_category]
    if new_model != '':
        bp_filter = new_model
    print("WARNING: Actor model {} not available. Using instead {}".format(model, new_model))
    blueprint = CarlaDataProvider._rng.choice(CarlaDataProvider._blueprint_library.filter(bp_filter))

    # Set the color
    if color:
        if not blueprint.has_attribute('color'):
            print(
                "WARNING: Cannot set Color ({}) for actor {} due to missing blueprint attribute".format(
                    color, blueprint.id))
        else:
            default_color_rgba = blueprint.get_attribute('color').as_color()
            default_color = '({}, {}, {})'.format(default_color_rgba.r, default_color_rgba.g, default_color_rgba.b)
            try:
                blueprint.set_attribute('color', color)
            except ValueError:
                # Color can't be set for this vehicle
                print("WARNING: Color ({}) cannot be set for actor {}. Using instead: ({})".format(
                    color, blueprint.id, default_color))
                blueprint.set_attribute('color', default_color)
    else:
        if blueprint.has_attribute('color') and rolename != 'hero':
            color = CarlaDataProvider._rng.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)

    # Make pedestrians mortal
    if blueprint.has_attribute('is_invincible'):
        blueprint.set_attribute('is_invincible', 'false')

    # Set the rolename
    if blueprint.has_attribute('role_name'):
        blueprint.set_attribute('role_name', rolename)

    return blueprint